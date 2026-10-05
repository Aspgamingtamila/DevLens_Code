"""C and C++ Deterministic Static Analyzer."""

import re
from typing import List, Tuple

from .base import BaseAnalyzer
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum
from ..schemas.metrics import AnalysisMetricSchema


class CppAnalyzer(BaseAnalyzer):
    def __init__(self, language: str = "cpp"):
        self._language = language

    @property
    def language_name(self) -> str:
        return self._language

    def analyze(self, code: str) -> Tuple[List[FindingSchema], AnalysisMetricSchema, str, str]:
        findings: List[FindingSchema] = []
        lines = code.splitlines()
        loc = len(lines)
        comment_lines = 0
        cyclomatic = 1
        max_loop_depth = 0
        current_loop_depth = 0
        has_recursion = False
        malloc_count = 0
        free_count = 0

        # Function detection for recursion
        function_names = set(re.findall(r"(?:void|int|char|bool|double|float|auto)\s+([A-Za-z0-9_]+)\s*\(", code))

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                comment_lines += 1

            # Branch counting for cyclomatic complexity
            branches = len(re.findall(r"\b(if|for|while|case|catch)\b|\&\&|\|\||\?", line))
            cyclomatic += branches

            # Loop depth tracking
            if re.search(r"\b(for|while)\s*\(", line):
                current_loop_depth += 1
                if current_loop_depth > max_loop_depth:
                    max_loop_depth = current_loop_depth
                if current_loop_depth >= 2:
                    findings.append(
                        FindingSchema(
                            severity=SeverityEnum.HIGH if current_loop_depth == 2 else SeverityEnum.CRITICAL,
                            category=CategoryEnum.COMPLEXITY,
                            source=SourceEnum.STATIC,
                            title=f"Nested loop detected (Depth {current_loop_depth})",
                            explanation=f"Nested loops create at least O(N^{current_loop_depth}) polynomial growth, which will bottleneck high-throughput routines.",
                            suggestion="Evaluate if data can be pre-sorted or mapped using std::unordered_map.",
                            line_start=idx,
                            line_end=idx,
                            rule_id="CPP-PERF-001",
                            confidence=0.9,
                        )
                    )
            if "}" in line and current_loop_depth > 0:
                current_loop_depth = max(0, current_loop_depth - line.count("}"))

            # Memory tracking
            if re.search(r"\b(malloc|calloc|realloc|new)\b", line):
                malloc_count += 1
            if re.search(r"\b(free|delete)\b", line):
                free_count += 1

            # Recursion detection
            for fn in function_names:
                if re.search(rf"\b{fn}\s*\(", line) and not re.search(rf"(?:void|int|char|bool|double|float|auto)\s+{fn}\s*\(", line):
                    has_recursion = True

            # 1. gets() inherently unsafe function
            if re.search(r"\bgets\s*\(", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Inherently unsafe function 'gets()' detected",
                        explanation="'gets()' performs no bounds checking and is the classic vector for stack-based buffer overflow exploits.",
                        suggestion="Replace 'gets()' with 'fgets(buf, sizeof(buf), stdin)'.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="CPP-SEC-001",
                        cwe_id="CWE-120",
                        confidence=1.0,
                    )
                )

            # 2. Unsafe string copy functions: strcpy, strcat, sprintf
            if re.search(r"\b(strcpy|strcat|sprintf)\s*\(", line):
                func = re.search(r"\b(strcpy|strcat|sprintf)\s*\(", line).group(1)
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title=f"Unbounded string operation via '{func}()'",
                        explanation=f"'{func}()' does not enforce destination buffer boundary checks, exposing the application to CWE-120 buffer overflow attacks.",
                        suggestion=f"Use bounded alternatives like 'strncpy', 'strncat', or 'snprintf' (or std::string in C++).",
                        line_start=idx,
                        line_end=idx,
                        rule_id="CPP-SEC-002",
                        cwe_id="CWE-120",
                        confidence=0.95,
                    )
                )

            # 3. Format string vulnerability
            if re.search(r"\bprintf\s*\(\s*[A-Za-z0-9_]+\s*\)", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.HIGH,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Potential Format String Vulnerability via non-literal printf argument",
                        explanation="Passing a variable directly as the format string in 'printf(var)' allows attackers to read or write arbitrary process memory via format specifiers (%x, %n).",
                        suggestion='Always specify a format literal: printf("%s", var);',
                        line_start=idx,
                        line_end=idx,
                        rule_id="CPP-SEC-003",
                        cwe_id="CWE-134",
                        confidence=0.9,
                    )
                )

        # Check for potential memory leaks
        if malloc_count > free_count:
            findings.append(
                FindingSchema(
                    severity=SeverityEnum.MEDIUM,
                    category=CategoryEnum.BUG,
                    source=SourceEnum.STATIC,
                    title=f"Potential Memory Leak ({malloc_count} allocations vs {free_count} deallocations)",
                    explanation="Dynamic memory allocated via malloc/new does not appear to have matching free/delete calls in this scope.",
                    suggestion="Ensure every allocated pointer is freed or use RAII smart pointers (std::unique_ptr, std::shared_ptr) in C++.",
                    line_start=1,
                    line_end=loc,
                    rule_id="CPP-BUG-001",
                    cwe_id="CWE-401",
                    confidence=0.8,
                )
            )

        # Big-O estimation
        if has_recursion:
            time_complexity = "O(2^N)" if max_loop_depth > 0 else "O(N)"
            space_complexity = "O(N)"
        elif max_loop_depth == 0:
            time_complexity = "O(1)"
            space_complexity = "O(1)"
        elif max_loop_depth == 1:
            time_complexity = "O(N)"
            space_complexity = "O(1)"
        elif max_loop_depth == 2:
            time_complexity = "O(N^2)"
            space_complexity = "O(1)"
        else:
            time_complexity = f"O(N^{max_loop_depth})"
            space_complexity = "O(1)"

        comment_ratio = comment_lines / max(loc, 1)
        crit_count = sum(1 for f in findings if f.severity == SeverityEnum.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == SeverityEnum.HIGH)
        med_count = sum(1 for f in findings if f.severity == SeverityEnum.MEDIUM)

        correctness = max(0.0, 100.0 - (crit_count * 20.0 + high_count * 10.0))
        security = max(0.0, 100.0 - sum(25.0 for f in findings if f.category == CategoryEnum.SECURITY))
        complexity_score = max(0.0, 100.0 - (max_loop_depth * 15.0 + max(0, cyclomatic - 5) * 5.0))
        readability = min(100.0, max(25.0, 80.0 + (comment_ratio * 30.0) - (crit_count * 10.0)))
        maintainability = max(10.0, 100.0 - (cyclomatic * 3.0 + (loc // 20) * 5.0))
        testing_score = max(30.0, 90.0 - (crit_count * 20.0 + med_count * 5.0))

        metrics = AnalysisMetricSchema(
            lines_of_code=loc,
            cyclomatic_complexity=cyclomatic,
            comment_ratio=round(comment_ratio, 4),
            maintainability_index=round(maintainability, 2),
            correctness_score=round(correctness, 2),
            security_score=round(security, 2),
            complexity_score=round(complexity_score, 2),
            readability_score=round(readability, 2),
            testing_score=round(testing_score, 2),
        )

        return findings, metrics, time_complexity, space_complexity
