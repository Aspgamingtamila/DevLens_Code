"""Analysis SQLAlchemy ORM Model."""

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.session import Base

if TYPE_CHECKING:
    from .finding import Finding
    from .generated_test import GeneratedTest
    from .metrics import AnalysisMetric
    from .user import User


def get_utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    user_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(255), default="Untitled Analysis", nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    code_snippet: Mapped[str] = mapped_column(Text, nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    quality_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    time_complexity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    space_complexity: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    is_saved: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="analyses")
    findings: Mapped[List["Finding"]] = relationship(
        "Finding", back_populates="analysis", cascade="all, delete-orphan", passive_deletes=True
    )
    metrics: Mapped[Optional["AnalysisMetric"]] = relationship(
        "AnalysisMetric",
        back_populates="analysis",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    generated_tests: Mapped[List["GeneratedTest"]] = relationship(
        "GeneratedTest",
        back_populates="analysis",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        Index("idx_analyses_user_created", "user_id", "created_at"),
        CheckConstraint("quality_score IS NULL OR (quality_score >= 0.0 AND quality_score <= 100.0)", name="chk_quality_score"),
    )
