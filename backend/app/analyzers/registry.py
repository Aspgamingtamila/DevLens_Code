"""Language Analyzer Registry.

Provides a unified lookup and registry for all supported programming languages.
"""

from typing import Dict
from .base import BaseAnalyzer
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .cpp_analyzer import CppAnalyzer
from .java_analyzer import JavaAnalyzer


class AnalyzerRegistry:
    def __init__(self):
        self._analyzers: Dict[str, BaseAnalyzer] = {}
        # Register default initial 6 languages
        self.register(PythonAnalyzer())
        self.register(JavaScriptAnalyzer("javascript"))
        self.register(JavaScriptAnalyzer("typescript"))
        self.register(CppAnalyzer("c"))
        self.register(CppAnalyzer("cpp"))
        self.register(JavaAnalyzer())

    def register(self, analyzer: BaseAnalyzer) -> None:
        """Registers a language analyzer instance."""
        self._analyzers[analyzer.language_name.lower()] = analyzer

    def get(self, language: str) -> BaseAnalyzer:
        """Retrieves analyzer for specified language. Defaults to Python if unknown."""
        normalized = language.strip().lower()
        if normalized not in self._analyzers:
            raise ValueError(f"No analyzer registered for language: '{language}'")
        return self._analyzers[normalized]


analyzer_registry = AnalyzerRegistry()
