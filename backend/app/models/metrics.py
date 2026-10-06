"""AnalysisMetric SQLAlchemy ORM Model."""

import uuid
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database.session import Base

if TYPE_CHECKING:
    from .analysis import Analysis


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AnalysisMetric(Base):
    __tablename__ = "analysis_metrics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    analysis_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    lines_of_code: Mapped[int] = mapped_column(Integer, nullable=False)
    cyclomatic_complexity: Mapped[int] = mapped_column(Integer, nullable=False)
    comment_ratio: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    maintainability_index: Mapped[float] = mapped_column(Float, nullable=False)
    correctness_score: Mapped[float] = mapped_column(Float, nullable=False)
    security_score: Mapped[float] = mapped_column(Float, nullable=False)
    complexity_score: Mapped[float] = mapped_column(Float, nullable=False)
    readability_score: Mapped[float] = mapped_column(Float, nullable=False)
    testing_score: Mapped[float] = mapped_column(Float, nullable=False)

    analysis: Mapped["Analysis"] = relationship("Analysis", back_populates="metrics")

    __table_args__ = (
        CheckConstraint("lines_of_code >= 0", name="chk_loc"),
        CheckConstraint("cyclomatic_complexity >= 1", name="chk_cyclomatic"),
        CheckConstraint("comment_ratio >= 0.0 AND comment_ratio <= 1.0", name="chk_comment_ratio"),
        CheckConstraint("maintainability_index >= 0.0 AND maintainability_index <= 100.0", name="chk_mi"),
        CheckConstraint("correctness_score >= 0.0 AND correctness_score <= 100.0", name="chk_correctness"),
        CheckConstraint("security_score >= 0.0 AND security_score <= 100.0", name="chk_security"),
        CheckConstraint("complexity_score >= 0.0 AND complexity_score <= 100.0", name="chk_complexity"),
        CheckConstraint("readability_score >= 0.0 AND readability_score <= 100.0", name="chk_readability"),
        CheckConstraint("testing_score >= 0.0 AND testing_score <= 100.0", name="chk_testing"),
    )
