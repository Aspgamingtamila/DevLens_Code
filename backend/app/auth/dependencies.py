"""Authentication dependencies for FastAPI endpoints."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .security import decode_access_token
from ..database.session import get_db
from ..models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def get_optional_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Optional[User]:
    """Retrieves authenticated User if a valid Bearer token is provided, otherwise None."""
    if not auth or not auth.credentials:
        return None

    payload = decode_access_token(auth.credentials)
    if not payload or "sub" not in payload:
        return None

    user_id = payload["sub"]
    stmt = select(User).where(User.id == user_id, User.is_active == True)
    result = db.execute(stmt)
    user = result.scalar_one_or_none()
    return user


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Enforces authentication. Raises 401 Unauthorized if invalid or missing token."""
    user = get_optional_user(auth=auth, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or session has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user
