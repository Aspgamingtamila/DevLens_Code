"""AI Provider Abstract Base Class and Structured Schemas."""

from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel, Field

from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum


class AIFinding(BaseModel):
    severity: SeverityEnum
    category: CategoryEnum
    title: str = Field(..., max_length=255)
    explanation: str
    suggestion: Optional[str] = None
    line_start: int = Field(..., ge=1)
    line_end: int = Field(..., ge=1)
    confidence: float = Field(0.85, ge=0.0, le=1.0)


class AITestCase(BaseModel):
    test_framework: str
    test_code: str
    explanation: Optional[str] = None


class AIStructuredOutput(BaseModel):
    summary: str
    findings: List[AIFinding] = []
    suggested_refactor: Optional[str] = None
    suggested_tests: List[AITestCase] = []
    limitations: List[str] = Field(
        default_factory=lambda: [
            "AI-generated suggestions are advisory recommendations and must be verified by developers."
        ]
    )


class AIProvider(ABC):
    """Abstract interface for AI code analysis providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the unique name of this provider (e.g. 'mock', 'gemini', 'openai')."""
        pass

    @abstractmethod
    async def analyze_code(
        self,
        code: str,
        language: str,
        static_findings: List[FindingSchema],
    ) -> AIStructuredOutput:
        """
        Synthesizes structured recommendations, refactoring suggestions, and unit tests.
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Checks if provider is accessible and properly configured."""
        pass
