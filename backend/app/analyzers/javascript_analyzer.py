"""JavaScript and TypeScript Deterministic Static Analyzer."""

import re
from typing import List, Tuple

from .base import BaseAnalyzer
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum
from ..schemas.metrics import AnalysisMetricSchema


class JavaScriptAnalyzer(BaseAnalyzer):
    def __init__(self, language: str = "javascript"):
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

        function_names = set(re.findall(r"function\s+([A-Za-z0-9_$]+)", code))
        function_names.update(re.findall(r"(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z0-9_$]+)\s*=>", code))

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
                comment_lines += 1

            # Branch counting for cyclomatic complexity
            branches = len(re.findall(r"\b(if|else if|for|while|case|catch)\b|\&\&|\|\||\?", line))
            cyclomatic += branches

            # Loop depth tracking
            if re.search(r"\b(for|while)\s*\(", line) or re.search(r"\.(forEach|map|filter)\s*\(", line):
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
                            explanation=f"Nested iteration creates at least O(N^{current_loop_depth}) complexity, which can cause frame drops or high latency on large datasets.",
                            suggestion="Consider Map/Set lookups, indexing, or memoized structures.",
                            line_start=idx,
                            line_end=idx,
                            rule_id="JS-PERF-001",
                            confidence=0.9,
                        )
                    )
            if "}" in line and current_loop_depth > 0:
                current_loop_depth = max(0, current_loop_depth - line.count("}"))

            # Recursion detection
            for fn in function_names:
                if re.search(rf"\b{fn}\s*\(", line) and not re.search(rf"function\s+{fn}", line) and not re.search(rf"{fn}\s*=", line):
                    has_recursion = True

            # 1. Dangerous eval()
            if re.search(r"\beval\s*\(", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Dangerous dynamic evaluation via 'eval()'",
                        explanation="Passing strings to 'eval()' permits execution of arbitrary JavaScript code and opens severe XSS/injection vulnerabilities.",
                        suggestion="Use JSON.parse() or structured logic instead of eval().",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JS-SEC-001",
                        cwe_id="CWE-95",
                        confidence=1.0,
                    )
                )

            # 2. XSS: innerHTML / outerHTML / document.write
            if re.search(r"\.(innerHTML|outerHTML)\s*=", line) or re.search(r"document\.write\s*\(", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.HIGH,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Cross-Site Scripting (XSS) risk via direct HTML injection",
                        explanation="Assigning untrusted or unescaped content to innerHTML allows malicious script injection in the user's browser context.",
                        suggestion="Use 'textContent', 'innerText', or sanitize with DOMPurify.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JS-SEC-002",
                        cwe_id="CWE-79",
                        confidence=0.95,
                    )
                )

            # 3. SQL Injection pattern
            if re.search(r"(SELECT|INSERT|UPDATE|DELETE)\s+.*(\+|\$\{)", line, re.IGNORECASE):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="SQL Injection risk via string concatenation",
                        explanation="Dynamic query concatenation without parameterization leaves the database vulnerable to SQL injection.",
                        suggestion="Use parameterized query placeholders ($1, ?) or an ORM like Prisma / TypeORM.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JS-SEC-003",
                        cwe_id="CWE-89",
                        confidence=0.9,
                    )
                )

            # 4. Loose equality (== instead of ===)
            if re.search(r"[^=!<>]==[^=]", line):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.LOW,
                        category=CategoryEnum.BUG,
                        source=SourceEnum.STATIC,
                        title="Loose equality operator '==' used instead of strict '==='",
                        explanation="The '==' operator performs implicit type coercion, leading to unexpected falsy comparisons (e.g. '' == 0 is true).",
                        suggestion="Use strict equality '===' to ensure both value and type match.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="JS-BUG-001",
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
