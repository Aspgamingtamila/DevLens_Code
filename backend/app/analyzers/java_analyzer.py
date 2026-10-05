"""Java Deterministic Static Analyzer."""

import re
from typing import List, Tuple

from .base import BaseAnalyzer
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum
from ..schemas.metrics import AnalysisMetricSchema


class JavaAnalyzer(BaseAnalyzer):
    @property
    def language_name(self) -> str:
        return "java"

    def analyze(self, code: str) -> Tuple[List[FindingSchema], AnalysisMetricSchema, str, str]:
        findings: List[FindingSchema] = []
        lines = code.splitlines()
        loc = len(lines)
        comment_lines = 0
        cyclomatic = 1
        max_loop_depth = 0
        current_loop_depth = 0
        has_recursion = False

        # Identify method names
        method_names = set(re.findall(r"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+([A-Za-z0-9_]+)\s*\(", code))

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                comment_lines += 1

            # Cyclomatic complexity branch counts
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
                            explanation=f"Nested loops create at least O(N^{current_loop_depth}) scaling, which can degrade throughput under high concurrent loads.",
                            suggestion="Consider HashMap indexing or Stream parallelization.",
                            line_start=idx,
                            line_end=idx,
                            rule_id="JAVA-PERF-001",
                            confidence=0.9,
                        )
                    )
            if "}" in line and current_loop_depth > 0:
                current_loop_depth = max(0, current_loop_depth - line.count("}"))

            # Recursion detection
            for m in method_names:
                if re.search(rf"\b{m}\s*\(", line) and not re.search(rf"(?:public|private|protected|static|\s)+[\w<>\[\]]+\s+{m}\s*\(", line):
                    has_recursion = True

            # 1. SQL Injection via string concatenation
            if re.search(r"(executeQuery|executeUpdate)\s*\(\s*.*(\+|\bString\.format\b)", line) or re.search(r"(SELECT|INSERT|UPDATE|DELETE)\s+.*(\+)", line, re.IGNORECASE):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="SQL Injection risk via dynamic query string concatenation",
                        explanation="Concatenating user variables into SQL queries bypasses JDBC type safety and permits SQL injection attacks.",
                        suggestion="Use PreparedStatement with parameter placeholders ('?') instead of direct string concatenation.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JAVA-SEC-001",
                        cwe_id="CWE-89",
                        confidence=0.95,
                    )
                )

            # 2. Information disclosure via printStackTrace()
            if re.search(r"\.printStackTrace\s*\(", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.LOW,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Information Disclosure risk via printStackTrace()",
                        explanation="Writing raw stack traces to standard output leaks internal classpaths and framework versions.",
                        suggestion="Log exceptions via a structured logger (e.g. SLF4J, Log4j2) with appropriate log levels.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JAVA-SEC-002",
                        cwe_id="CWE-209",
                        confidence=0.9,
                    )
                )

            # 3. Generic catch (Exception e)
            if re.search(r"catch\s*\(\s*Exception\s+\w+\s*\)", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.MEDIUM,
                        category=CategoryEnum.BUG,
                        source=SourceEnum.STATIC,
                        title="Generic 'catch (Exception e)' catches all exceptions indiscriminately",
                        explanation="Catching java.lang.Exception catches RuntimeExceptions and masks underlying logic errors.",
                        suggestion="Catch specific checked exceptions (e.g., IOException, SQLException).",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JAVA-BUG-001",
                        cwe_id="CWE-396",
                        confidence=0.85,
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
