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

        if self._language in ("c", "cpp"):
            def add_finding(rule_id: str, title: str, explanation: str, suggestion: str, line: int, severity: SeverityEnum = SeverityEnum.HIGH) -> None:
                findings.append(
                    FindingSchema(
                        severity=severity,
                        category=CategoryEnum.BUG,
                        source=SourceEnum.STATIC,
                        title=title,
                        explanation=explanation,
                        suggestion=suggestion,
                        line_start=line,
                        line_end=line,
                        rule_id=rule_id,
                        confidence=0.95,
                    )
                )

            standard_header_typo = re.compile(
                r"\b(?:stdio|stdlib|string|stdint|stdbool|stddef|time|math|ctype|errno|assert|limits|float|signal|locale|wchar|wctype),h\b",
                re.IGNORECASE,
            )
            for line_number, line in enumerate(lines, start=1):
                include = re.match(r"\s*#\s*include\s*[<\"]([^>\"]+)[>\"]", line)
                if include and standard_header_typo.search(include.group(1)):
                    header = include.group(1)
                    add_finding(
                        "C-SYNTAX-001",
                        f"Malformed standard header name: <{header}>",
                        "The standard header name is malformed, so the compiler cannot find the header.",
                        "Use the correct header spelling, such as #include <stdio.h>.",
                        line_number,
                        SeverityEnum.CRITICAL,
                    )

            main_declaration = re.search(r"(?m)^\s*(?:void|int)\s+main\s*\([^;{}]*\)\s*;", code)
            has_main_definition = re.search(r"\b(?:void|int)\s+main\s*\([^;{}]*\)\s*\{", code)
            has_function_definition = re.search(
                r"\b(?:void|char|short|int|long|float|double|_Bool|bool)\s+[A-Za-z_]\w*\s*\([^;{}]*\)\s*\{",
                code,
            )

            void_main = re.search(r"\bvoid\s+main\s*\(", code)
            if void_main:
                line_number = code.count("\n", 0, void_main.start()) + 1
                add_finding(
                    "C-BUG-MAIN-001",
                    "Non-standard return type for main()",
                    "A hosted C or C++ program expects main() to return int; void main() is not standard.",
                    "Declare the entry point as int main(void) and return an integer status.",
                    line_number,
                    SeverityEnum.MEDIUM,
                )

            if main_declaration and not has_main_definition:
                line_number = code.count("\n", 0, main_declaration.start()) + 1
                add_finding(
                    "C-SYNTAX-002",
                    "main() is declared but never defined",
                    "This line is only a function declaration. The following standalone block is not the body of main().",
                    "Remove the semicolon after the main() signature and place the opening brace directly after the signature.",
                    line_number,
                    SeverityEnum.CRITICAL,
                )

                block = re.search(r"(?m)^\s*\{\s*$", code[main_declaration.end():])
                if block:
                    line_number = code.count("\n", 0, main_declaration.end() + block.start()) + 1
                    add_finding(
                        "C-SYNTAX-003",
                        "Unexpected block outside a function",
                        "A brace block at file scope cannot contain C or C++ statements. It looks like this block was intended to be main()'s body.",
                        "Move the opening brace before the statements and remove the semicolon from the main() definition.",
                        line_number,
                        SeverityEnum.CRITICAL,
                    )

            if main_declaration and not has_function_definition:
                for match in re.finditer(r"\breturn\b", code):
                    line_number = code.count("\n", 0, match.start()) + 1
                    add_finding(
                        "C-SYNTAX-004",
                        "return used outside a function",
                        "C and C++ return statements must appear inside a function body; this block is at file scope.",
                        "Put the statements inside the main() function body.",
                        line_number,
                        SeverityEnum.CRITICAL,
                    )

            if self._language == "c":
                declarations = {
                    match.group(2): bool(match.group(1))
                    for match in re.finditer(
                        r"\b(?:int|float|double|_Bool|bool)\s+(\*+\s*)?([A-Za-z_]\w*)\s*(?:=[^;\n]*)?;",
                        code,
                    )
                }
                for match in re.finditer(r"\b([A-Za-z_]\w*)\s*=\s*\"(?:\\.|[^\"\\])*\"", code):
                    if match.group(1) in declarations and not declarations[match.group(1)]:
                        line_number = code.count("\n", 0, match.start()) + 1
                        add_finding(
                            "C-BUG-TYPE-001",
                            f"String assigned to integer variable '{match.group(1)}'",
                            f"The variable '{match.group(1)}' is declared as an integer, but this assignment provides a string literal.",
                            "Use a char array or a char pointer for text, or assign a numeric value to the integer.",
                            line_number,
                            SeverityEnum.CRITICAL,
                        )

                print_call = re.search(r"\bprint\s*\(", code)
                print_declaration = re.search(r"\b(?:void|int|char|short|long|float|double)\s+print\s*\(", code)
                if print_call and not print_declaration:
                    line_number = code.count("\n", 0, print_call.start()) + 1
                    add_finding(
                        "C-BUG-UNDECLARED-001",
                        "Unknown function: print()",
                        "print() is not part of the C standard library and no declaration for it appears in this code.",
                        "Use printf() from <stdio.h>, or declare and define your own print() function.",
                        line_number,
                    )

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
