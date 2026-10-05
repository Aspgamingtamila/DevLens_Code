"""Finding SQLAlchemy ORM Model."""

import uuid
from typing import Optional
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Finding(Base):
    __tablename__ = "findings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True
    )
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    category: Mapped[str] = mapped_column(String(30), nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    suggestion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    line_start: Mapped[int] = mapped_column(Integer, nullable=False)
    line_end: Mapped[int] = mapped_column(Integer, nullable=False)
    column_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    column_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rule_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cwe_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="findings")

    __table_args__ = (
        Index("idx_findings_analysis_severity", "analysis_id", "severity"),
        Index("idx_findings_analysis_category", "analysis_id", "category"),
        CheckConstraint("severity IN ('critical', 'high', 'medium', 'low', 'info')", name="chk_severity"),
        CheckConstraint("category IN ('bug', 'security', 'complexity', 'style', 'maintainability')", name="chk_category"),
        CheckConstraint("source IN ('static', 'ai', 'hybrid')", name="chk_source"),
        CheckConstraint("line_start >= 1", name="chk_line_start"),
        CheckConstraint("line_end >= line_start", name="chk_line_end"),
        CheckConstraint("confidence >= 0.0 AND confidence <= 1.0", name="chk_confidence"),
    )
