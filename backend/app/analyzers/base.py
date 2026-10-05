"""Base class and common models for deterministic language static analyzers."""

from abc import ABC, abstractmethod
from typing import List, Tuple
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum
from ..schemas.metrics import AnalysisMetricSchema


class BaseAnalyzer(ABC):
    """Abstract base class for all deterministic language analyzers."""

    @property
    @abstractmethod
    def language_name(self) -> str:
        """Returns the canonical language name (e.g., 'python', 'javascript')."""
        pass

    @abstractmethod
    def analyze(self, code: str) -> Tuple[List[FindingSchema], AnalysisMetricSchema, str, str]:
        """
        Executes deterministic static analysis on code snippet.
        Returns:
            findings: List of deterministic issues (bugs, security, complexity, style)
            metrics: Structural metrics (LOC, cyclomatic complexity, maintainability)
            time_complexity: Big-O time complexity estimate (e.g. 'O(N)')
            space_complexity: Big-O space complexity estimate (e.g. 'O(1)')
        """
        pass
