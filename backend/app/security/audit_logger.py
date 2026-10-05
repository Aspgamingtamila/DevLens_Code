"""Audit logging service for security and compliance."""

import hashlib
from typing import Optional
from sqlalchemy.orm import Session

from ..models.audit import AuditEvent
from ..logging import logger


SALT = "devlens_audit_privacy_salt"


def hash_ip(ip: Optional[str]) -> Optional[str]:
    """Generates a privacy-preserving salted SHA-256 hash of an IP address."""
    if not ip:
        return None
    return hashlib.sha256(f"{ip}:{SALT}".encode("utf-8")).hexdigest()


def record_audit_event(
    db: Session,
    user_id: str,
    event_type: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """Writes a security audit event to the database."""
    try:
        event = AuditEvent(
            user_id=user_id,
            event_type=event_type,
            ip_hash=hash_ip(ip_address),
            user_agent=user_agent[:255] if user_agent else None,
        )
        db.add(event)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to record audit event '{event_type}' for user {user_id}: {e}")
