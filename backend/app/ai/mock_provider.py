"""Hermetic Offline Mock AI Provider for testing and offline environments."""

from typing import List
from .base import AIProvider, AIStructuredOutput, AIFinding, AITestCase
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum


class MockAIProvider(AIProvider):
    @property
    def provider_name(self) -> str:
        return "mock"

    async def health_check(self) -> bool:
        return True

    async def analyze_code(
        self,
        code: str,
        language: str,
        static_findings: List[FindingSchema],
    ) -> AIStructuredOutput:
        norm_lang = language.lower()
        findings: List[AIFinding] = []
        tests: List[AITestCase] = []

        # Educational AI finding based on static findings or general clean-code principles
        if any(f.category == CategoryEnum.SECURITY for f in static_findings):
            findings.append(
                AIFinding(
                    severity=SeverityEnum.HIGH,
                    category=CategoryEnum.SECURITY,
                    title="Defensive Engineering Recommendation",
                    explanation="One or more potential security vulnerabilities were detected in static analysis. Implement input sanitization and defensive validation before passing variables to sensitive sinks.",
                    suggestion="Adopt the Principle of Least Privilege and validate all inputs against strict type/range schemas.",
                    line_start=1,
                    line_end=1,
                    confidence=0.88,
                )
            )
        else:
            findings.append(
                AIFinding(
                    severity=SeverityEnum.INFO,
                    category=CategoryEnum.MAINTAINABILITY,
                    title="Type Annotations & Documentation Enhancement",
                    explanation="Explicit type signatures and docstrings improve developer ergonomics, maintainability, and allow static analyzers to catch defects earlier.",
                    suggestion="Add descriptive documentation and return type annotations to all public functions.",
                    line_start=1,
                    line_end=1,
                    confidence=0.85,
                )
            )

        # Generate framework-specific test templates
        if norm_lang == "python":
            framework = "pytest"
            test_code = (
                "import pytest\n\n"
                "# Test happy path execution\n"
                "def test_happy_path():\n"
                "    # Replace with function call and expected output\n"
                "    assert True\n\n"
                "# Test edge case with boundary inputs (None, empty, negative)\n"
                "def test_boundary_conditions():\n"
                "    with pytest.raises((ValueError, TypeError)):\n"
                "        # Trigger boundary validation\n"
                "        pass\n"
            )
        elif norm_lang in ("javascript", "typescript"):
            framework = "vitest"
            test_code = (
                "import { describe, it, expect } from 'vitest';\n\n"
                "describe('Routine Unit Tests', () => {\n"
                "  it('should handle standard valid inputs correctly', () => {\n"
                "    expect(true).toBe(true);\n"
                "  });\n\n"
                "  it('should handle empty or null inputs gracefully', () => {\n"
                "    expect(() => {\n"
                "      // invoke boundary case\n"
                "    }).toThrow();\n"
                "  });\n"
                "});\n"
            )
        elif norm_lang == "java":
            framework = "junit5"
            test_code = (
                "import org.junit.jupiter.api.Test;\n"
                "import static org.junit.jupiter.api.Assertions.*;\n\n"
                "public class RoutineTest {\n"
                "    @Test\n"
                "    void testStandardExecution() {\n"
                "        assertTrue(true);\n"
                "    }\n\n"
                "    @Test\n"
                "    void testBoundaryNullInput() {\n"
                "        assertThrows(IllegalArgumentException.class, () -> {\n"
                "            // trigger exception\n"
                "        });\n"
                "    }\n"
                "}\n"
            )
        else:  # c, cpp
            framework = "googletest"
            test_code = (
                "#include <gtest/gtest.h>\n\n"
                "TEST(RoutineTest, HandlesStandardInput) {\n"
                "    EXPECT_EQ(1, 1);\n"
                "}\n\n"
                "TEST(RoutineTest, HandlesBoundaryConditions) {\n"
                "    EXPECT_NO_THROW({\n"
                "        // test boundary execution\n"
                "    });\n"
                "}\n"
            )

        tests.append(
            AITestCase(
                test_framework=framework,
                test_code=test_code,
                explanation=f"Synthesized {framework} test suite verifying happy path execution and boundary error handling.",
            )
        )

        return AIStructuredOutput(
            summary=f"Analysis of {language.upper()} code completed with deterministic static heuristics and mock educational synthesis.",
            findings=findings,
            suggested_refactor="// Review the suggested improvements tab for modular refactoring.",
            suggested_tests=tests,
            limitations=[
                "DevLens Quality Estimate is an advisory heuristic. AI suggestions are automated recommendations and must be verified by developers."
            ],
        )
