"""Analysis Request, Response, and Export Pydantic schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from .findings import FindingSchema
from .metrics import AnalysisMetricSchema


SUPPORTED_LANGUAGES = {"c", "cpp", "python", "java", "javascript", "typescript"}


class AnalysisRequest(BaseModel):
    title: Optional[str] = Field("Untitled Analysis", max_length=255)
    language: str = Field(..., description="Target language: c, cpp, python, java, javascript, typescript")
    code: str = Field(..., min_length=1, max_length=10000, description="Source code snippet up to 10,000 characters")
    save_history: bool = Field(True, description="Whether to save analysis to user history if authenticated")

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        normalized = v.strip().lower()
        if normalized not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language '{v}'. Supported: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
            )
        return normalized

    @field_validator("code")
    @classmethod
    def validate_code_lines(cls, v: str) -> str:
        lines = v.splitlines()
        if len(lines) > 500:
            raise ValueError(f"Code exceeds maximum 500 lines limit (received {len(lines)} lines).")
        return v


class GeneratedTestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    test_framework: str
    test_code: str
    explanation: Optional[str] = None
    created_at: Optional[datetime] = None


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    language: str
    code_snippet: str
    quality_score: float
    summary: str
    time_complexity: str
    space_complexity: str
    findings: List[FindingSchema]
    metrics: Optional[AnalysisMetricSchema] = None
    generated_tests: List[GeneratedTestSchema] = []
    created_at: datetime
    is_saved: bool
    disclaimer: str = (
        "DevLens Quality Estimate is an advisory heuristic. AI suggestions are "
        "recommendations and must be verified by developers."
    )


class AnalysisSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    language: str
    quality_score: Optional[float] = None
    findings_count: int
    created_at: datetime
