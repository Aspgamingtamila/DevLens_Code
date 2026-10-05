"""AuditEvent SQLAlchemy ORM Model for security and compliance tracking."""

import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.session import Base


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )

    user: Mapped["User"] = relationship("User", back_populates="audit_events")

    __table_args__ = (
        Index("idx_audit_events_user_created", "user_id", "created_at"),
        CheckConstraint(
            "event_type IN ('LOGIN', 'REGISTER', 'ANALYSIS_CREATED', 'ANALYSIS_DELETED', 'ACCOUNT_DELETED', 'EXPORT')",
            name="chk_event_type",
        ),
    )
