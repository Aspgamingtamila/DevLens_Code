"""Python Deterministic Static Analyzer using native AST visitor and structural metrics."""

import ast
import re
from typing import List, Tuple

from .base import BaseAnalyzer
from ..schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum
from ..schemas.metrics import AnalysisMetricSchema


class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.findings: List[FindingSchema] = []
        self.cyclomatic_complexity: int = 1
        self.loop_depth: int = 0
        self.max_loop_depth: int = 0
        self.has_recursion: bool = False
        self.function_names: set = set()
        self.current_function: str = ""

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.function_names.add(node.name)
        old_fn = self.current_function
        self.current_function = node.name
        
        # Check function length
        fn_lines = (node.end_lineno or node.lineno) - node.lineno + 1
        if fn_lines > 50:
            self.findings.append(
                FindingSchema(
                    severity=SeverityEnum.MEDIUM,
                    category=CategoryEnum.MAINTAINABILITY,
                    source=SourceEnum.STATIC,
                    title=f"Function '{node.name}' is too long ({fn_lines} lines)",
                    explanation="Functions longer than 50 lines increase cognitive burden and reduce testability.",
                    suggestion="Decompose this function into smaller, single-purpose helper functions.",
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    rule_id="PY-MAINT-001",
                    confidence=1.0,
                )
            )
            
        self.generic_visit(node)
        self.current_function = old_fn

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)  # type: ignore

    def visit_If(self, node: ast.If):
        self.cyclomatic_complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For):
        self.cyclomatic_complexity += 1
        self.loop_depth += 1
        if self.loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.loop_depth
            
        if self.loop_depth >= 2:
            self.findings.append(
                FindingSchema(
                    severity=SeverityEnum.HIGH if self.loop_depth == 2 else SeverityEnum.CRITICAL,
                    category=CategoryEnum.COMPLEXITY,
                    source=SourceEnum.STATIC,
                    title=f"Nested loop detected (Depth {self.loop_depth})",
                    explanation=f"Nested loop of depth {self.loop_depth} indicates at least O(N^{self.loop_depth}) polynomial scaling, which can degrade performance on large datasets.",
                    suggestion="Consider refactoring with dictionaries, hash sets, or vectorized operations.",
                    line_start=node.lineno,
                    line_end=node.end_lineno or node.lineno,
                    rule_id="PY-PERF-001",
                    confidence=1.0,
                )
            )
            
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_While(self, node: ast.While):
        self.cyclomatic_complexity += 1
        self.loop_depth += 1
        if self.loop_depth > self.max_loop_depth:
            self.max_loop_depth = self.loop_depth
            
        self.generic_visit(node)
        self.loop_depth -= 1

    def visit_ExceptHandler(self, node: ast.ExceptHandler):
        self.cyclomatic_complexity += 1
        if node.type is None:
            self.findings.append(
                FindingSchema(
                    severity=SeverityEnum.MEDIUM,
                    category=CategoryEnum.BUG,
                    source=SourceEnum.STATIC,
                    title="Bare 'except:' clause without explicit exception type",
                    explanation="Catching all exceptions indiscriminately masks KeyboardInterrupt, SystemExit, and unexpected runtime bugs.",
                    suggestion="Specify the exact exception class, e.g. 'except ValueError:' or 'except Exception:' at minimum.",
                    line_start=node.lineno,
                    line_end=node.lineno,
                    rule_id="PY-BUG-001",
                    cwe_id="CWE-396",
                    confidence=1.0,
                )
            )
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        # Recursion check
        if isinstance(node.func, ast.Name):
            if node.func.id == self.current_function and self.current_function != "":
                self.has_recursion = True

            # Detect dangerous built-ins: eval, exec
            if node.func.id in ("eval", "exec"):
                self.findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title=f"Dangerous dynamic code execution via '{node.func.id}()'",
                        explanation=f"Calling '{node.func.id}()' allows arbitrary code execution if untrusted input is passed, creating severe remote code execution vulnerabilities.",
                        suggestion="Avoid dynamic execution; use structured parsers like 'ast.literal_eval()' or JSON parsing.",
                        line_start=node.lineno,
                        line_end=node.lineno,
                        rule_id="PY-SEC-001",
                        cwe_id="CWE-95",
                        confidence=1.0,
                    )
                )

        # Detect subprocess with shell=True
        if isinstance(node.func, ast.Attribute) and node.func.attr in ("Popen", "call", "run", "check_output"):
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant) and keyword.value.value is True:
                    self.findings.append(
                        FindingSchema(
                            severity=SeverityEnum.CRITICAL,
                            category=CategoryEnum.SECURITY,
                            source=SourceEnum.STATIC,
                            title="Command Injection risk: 'subprocess' invoked with 'shell=True'",
                            explanation="Executing system commands with 'shell=True' allows command injection if any part of the command string is user-controllable.",
                            suggestion="Pass command arguments as a list and set 'shell=False'.",
                            line_start=node.lineno,
                            line_end=node.lineno,
                            rule_id="PY-SEC-002",
                            cwe_id="CWE-78",
                            confidence=1.0,
                        )
                    )

        self.generic_visit(node)


class PythonAnalyzer(BaseAnalyzer):
    @property
    def language_name(self) -> str:
        return "python"

    def analyze(self, code: str) -> Tuple[List[FindingSchema], AnalysisMetricSchema, str, str]:
        findings: List[FindingSchema] = []
        lines = code.splitlines()
        loc = len(lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
        comment_ratio = comment_lines / max(loc, 1)

        # 1. Regex & Pattern Checks for SQLi and Hardcoded Secrets
        for idx, line in enumerate(lines, start=1):
            # SQL Injection heuristics (string interpolation or f-strings in query strings)
            if re.search(r"(SELECT|INSERT|UPDATE|DELETE)\s+.*(\%s|\{.*?\}|\.format|\+\s*\w+)", line, re.IGNORECASE):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.CRITICAL,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Potential SQL Injection via dynamic string interpolation",
                        explanation="Constructing SQL queries using string formatting or concatenation exposes the database to SQL injection attacks.",
                        suggestion="Use parameterized queries with bind variables or an ORM.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="PY-SEC-003",
                        cwe_id="CWE-89",
                        confidence=0.9,
                    )
                )

            # Hardcoded Secrets heuristic
            if re.search(r"(api_key|password|secret|auth_token)\s*=\s*['\"][A-Za-z0-9_\-\.]{12,}['\"]", line, re.IGNORECASE):
                findings.append(
                    FindingSchema(
                        severity=SeverityEnum.HIGH,
                        category=CategoryEnum.SECURITY,
                        source=SourceEnum.STATIC,
                        title="Hardcoded API key or credential detected",
                        explanation="Embedding credentials directly in source code risks accidental exposure in public repositories.",
                        suggestion="Load credentials from environment variables or a secrets manager.",
                        line_start=idx,
                        line_end=idx,
                        rule_id="PY-SEC-004",
                        cwe_id="CWE-798",
                        confidence=0.95,
                    )
                )

        # 2. Native AST Parsing
        try:
            tree = ast.parse(code, filename="<untrusted_snippet>", mode="exec")
            visitor = PythonASTVisitor()
            visitor.visit(tree)
            findings.extend(visitor.findings)
            cyclomatic = visitor.cyclomatic_complexity
            max_depth = visitor.max_loop_depth
            has_recursion = visitor.has_recursion
        except SyntaxError as e:
            findings.append(
                FindingSchema(
                    severity=SeverityEnum.CRITICAL,
                    category=CategoryEnum.BUG,
                    source=SourceEnum.STATIC,
                    title=f"Syntax Error: {e.msg}",
                    explanation=f"Python parser failed at line {e.lineno}, column {e.offset}: {e.text or ''}",
                    suggestion="Verify indentation, colons, brackets, and syntax correctness.",
                    line_start=e.lineno or 1,
                    line_end=e.lineno or 1,
                    column_start=e.offset,
                    column_end=e.offset,
                    rule_id="PY-SYNTAX-001",
                    confidence=1.0,
                )
            )
            cyclomatic = 1
            max_depth = 0
            has_recursion = False

        # 3. Big-O Complexity Estimation
        if has_recursion:
            time_complexity = "O(2^N)" if max_depth > 0 else "O(N)"
            space_complexity = "O(N)"  # recursion call stack
        elif max_depth == 0:
            time_complexity = "O(1)"
            space_complexity = "O(1)"
        elif max_depth == 1:
            time_complexity = "O(N)"
            space_complexity = "O(1)"
        elif max_depth == 2:
            time_complexity = "O(N^2)"
            space_complexity = "O(1)"
        else:
            time_complexity = f"O(N^{max_depth})"
            space_complexity = "O(1)"

        # 4. Scores Calculation
        crit_count = sum(1 for f in findings if f.severity == SeverityEnum.CRITICAL)
        high_count = sum(1 for f in findings if f.severity == SeverityEnum.HIGH)
        med_count = sum(1 for f in findings if f.severity == SeverityEnum.MEDIUM)

        correctness = max(0.0, 100.0 - (crit_count * 20.0 + high_count * 10.0))
        security = max(0.0, 100.0 - sum(25.0 for f in findings if f.category == CategoryEnum.SECURITY))
        complexity_score = max(0.0, 100.0 - (max_depth * 15.0 + max(0, cyclomatic - 5) * 5.0))
        readability = min(100.0, max(20.0, 80.0 + (comment_ratio * 30.0) - (crit_count * 10.0)))
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
