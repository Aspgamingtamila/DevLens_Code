"""Finding and Diagnostic Pydantic schemas."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SeverityEnum(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CategoryEnum(str, Enum):
    BUG = "bug"
    SECURITY = "security"
    COMPLEXITY = "complexity"
    STYLE = "style"
    MAINTAINABILITY = "maintainability"


class SourceEnum(str, Enum):
    STATIC = "static"
    AI = "ai"
    HYBRID = "hybrid"


class FindingSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    severity: SeverityEnum
    category: CategoryEnum
    source: SourceEnum
    title: str = Field(..., max_length=255)
    explanation: str
    suggestion: Optional[str] = None
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)
    column_start: Optional[int] = Field(None, ge=1)
    column_end: Optional[int] = Field(None, ge=1)
    rule_id: Optional[str] = None
    cwe_id: Optional[str] = None
    confidence: float = Field(1.0, ge=0.0, le=1.0)
