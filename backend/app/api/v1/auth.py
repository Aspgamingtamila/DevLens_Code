"""Authentication API endpoints."""

import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ...auth.dependencies import get_current_user
from ...auth.security import (
    create_access_token,
    generate_random_token,
    hash_password,
    hash_token,
    verify_password,
)
from ...config import settings
from ...database.session import get_db
from ...models.user import RefreshToken, User
from ...schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from ...schemas.user import UserResponse
from ...security.audit_logger import record_audit_event
from ...security.rate_limiter import rate_limit_auth

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED, dependencies=[Depends(rate_limit_auth)])
def register(
    payload: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Registers a new user and returns JWT access and refresh tokens."""
    # Check if email is already registered
    stmt = select(User).where(User.email == payload.email.lower().strip())
    result = db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    user_id = str(uuid.uuid4())
    hashed_pwd = hash_password(payload.password)
    user = User(
        id=user_id,
        email=payload.email.lower().strip(),
        hashed_password=hashed_pwd,
        full_name=payload.full_name.strip(),
        is_active=True,
        is_verified=False,
    )
    db.add(user)

    # Issue tokens
    access_token = create_access_token(subject=user_id, extra_claims={"email": user.email})
    raw_refresh = generate_random_token()
    refresh_record = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user_id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(refresh_record)
    db.commit()

    # Log audit event
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    record_audit_event(db, user_id=user_id, event_type="REGISTER", ip_address=client_ip, user_agent=user_agent)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=raw_refresh,
    )


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(rate_limit_auth)])
def login(
    payload: LoginRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Authenticates user credentials and issues tokens."""
    stmt = select(User).where(User.email == payload.email.lower().strip())
    result = db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deactivated.",
        )

    # Issue tokens
    access_token = create_access_token(subject=user.id, extra_claims={"email": user.email})
    raw_refresh = generate_random_token()
    refresh_record = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=hash_token(raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(refresh_record)
    db.commit()

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    record_audit_event(db, user_id=user.id, event_type="LOGIN", ip_address=client_ip, user_agent=user_agent)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=raw_refresh,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    """Rotates refresh token and returns a new access token."""
    hashed = hash_token(payload.refresh_token)
    stmt = select(RefreshToken).where(RefreshToken.token_hash == hashed, RefreshToken.revoked.is_(False))
    result = db.execute(stmt)
    token_record = result.scalar_one_or_none()

    expires_at = token_record.expires_at if token_record else None
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if not token_record or (expires_at and expires_at < datetime.now(timezone.utc)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is expired or invalid.",
        )

    # Invalidate current refresh token (Rotation)
    token_record.revoked = True

    # Retrieve user
    user_stmt = select(User).where(User.id == token_record.user_id, User.is_active.is_(True))
    user_res = db.execute(user_stmt)
    user = user_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")

    # Issue fresh tokens
    new_access = create_access_token(subject=user.id, extra_claims={"email": user.email})
    new_raw_refresh = generate_random_token()
    new_refresh_record = RefreshToken(
        id=str(uuid.uuid4()),
        user_id=user.id,
        token_hash=hash_token(new_raw_refresh),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        revoked=False,
    )
    db.add(new_refresh_record)
    db.commit()

    return TokenResponse(
        access_token=new_access,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=new_raw_refresh,
    )


@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
):
    """Returns authenticated user profile information."""
    return current_user


@router.delete("/me", response_model=MessageResponse)
def delete_my_account(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently deletes the authenticated user account and all associated analyses (GDPR)."""
    user_id = current_user.id
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    record_audit_event(db, user_id=user_id, event_type="ACCOUNT_DELETED", ip_address=client_ip, user_agent=user_agent)

    # Cascading deletion cleanly eliminates user, sessions, analyses, findings, and metrics
    db.delete(current_user)
    db.commit()

    return MessageResponse(message="Account and all associated analyses have been permanently purged.")
