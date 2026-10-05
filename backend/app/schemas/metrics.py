"""Metrics and DevLens Quality Estimate schemas."""

from pydantic import BaseModel, ConfigDict, Field


class AnalysisMetricSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lines_of_code: int = Field(..., ge=0)
    cyclomatic_complexity: int = Field(..., ge=1)
    comment_ratio: float = Field(0.0, ge=0.0, le=1.0)
    maintainability_index: float = Field(..., ge=0.0, le=100.0)
    correctness_score: float = Field(..., ge=0.0, le=100.0)
    security_score: float = Field(..., ge=0.0, le=100.0)
    complexity_score: float = Field(..., ge=0.0, le=100.0)
    readability_score: float = Field(..., ge=0.0, le=100.0)
    testing_score: float = Field(..., ge=0.0, le=100.0)


class QualityScoreSchema(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Advisory DevLens Quality Estimate (DQE)")
    grade: str = Field(..., description="Letter grade A, B, C, D, F")
    metrics: AnalysisMetricSchema
    disclaimer: str = (
        "DevLens Quality Estimate is an advisory heuristic. AI-generated suggestions "
        "and generated tests are recommendations and must be verified by developers."
    )
