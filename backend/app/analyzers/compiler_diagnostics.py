"""Run compiler or parser checks without executing submitted code."""

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

from ..schemas.findings import CategoryEnum, FindingSchema, SeverityEnum, SourceEnum


_INCLUDE_DIRECTIVE = re.compile(r"(?m)^[ \t]*#[ \t]*include(?:_next)?[ \t]*(.+?)[ \t]*$")


def _finding(
    language: str,
    severity: SeverityEnum,
    title: str,
    explanation: str,
    line: int = 1,
    column: int = 1,
    rule_suffix: str = "DIAGNOSTIC",
) -> FindingSchema:
    return FindingSchema(
        severity=severity,
        category=CategoryEnum.BUG,
        source=SourceEnum.STATIC,
        title=title[:255],
        explanation=explanation,
        suggestion="Review the compiler diagnostic and correct the code at the reported location.",
        line_start=max(1, line),
        line_end=max(1, line),
        column_start=max(1, column),
        column_end=max(1, column),
        rule_id=f"{language.upper()}-COMPILER-{rule_suffix}",
        confidence=1.0,
    )


def _unavailable(language: str, message: str) -> FindingSchema:
    return FindingSchema(
        severity=SeverityEnum.INFO,
        category=CategoryEnum.BUG,
        source=SourceEnum.STATIC,
        title=f"Full compiler diagnostics unavailable for {language.upper()}",
        explanation=message,
        suggestion="Run DevLens with its Docker Compose backend to enable compiler diagnostics.",
        line_start=1,
        line_end=1,
        rule_id=f"{language.upper()}-COMPILER-UNAVAILABLE",
        confidence=1.0,
    )


def _c_include_safety_message(code: str) -> str | None:
    for match in _INCLUDE_DIRECTIVE.finditer(code):
        include = match.group(1).strip()
        if include.startswith(("<", '"')) and len(include) > 2:
            path = include[1:-1]
            if not path.startswith(("/", "\\")) and not re.match(r"^[A-Za-z]:", path):
                if "\\" not in path and all(part != ".." for part in Path(path).parts):
                    continue
        line = code.count("\n", 0, match.start()) + 1
        return f"Compiler checking was skipped because the include on line {line} can access files outside the submitted snippet."
    return None


def _run(
    command: List[str],
    language: str,
    cwd: str | None = None,
    code: str | None = None,
) -> Tuple[List[FindingSchema], bool]:
    try:
        result = subprocess.run(
            command,
            input=code,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=8,
            cwd=cwd,
            env={**os.environ, "LC_ALL": "C", "GCC_COLORS": "never", "JAVA_TOOL_OPTIONS": ""},
            check=False,
        )
    except FileNotFoundError:
        return [_unavailable(language, f"The required compiler ({command[0]}) is not installed on this backend.")], False
    except subprocess.TimeoutExpired:
        return [
            _finding(
                language,
                SeverityEnum.INFO,
                f"{language.upper()} compiler check timed out",
                "The compile-only check exceeded its eight-second limit, so the code could not be fully checked.",
                rule_suffix="TIMEOUT",
            )
        ], False

    output = result.stderr[:65536]
    findings: List[FindingSchema] = []

    if language in ("c", "cpp"):
        pattern = re.compile(r"^(?:<stdin>|[^:\n]+):(\d+)(?::(\d+))?:\s*(fatal error|error|warning|note):\s*(.+)$")
        for line in output.splitlines():
            match = pattern.match(line.strip())
            if not match:
                continue
            kind = match.group(3)
            severity = {
                "fatal error": SeverityEnum.CRITICAL,
                "error": SeverityEnum.CRITICAL,
                "warning": SeverityEnum.MEDIUM,
                "note": SeverityEnum.INFO,
            }[kind]
            findings.append(
                _finding(
                    language,
                    severity,
                    f"{kind.title()}: {match.group(4)}",
                    f"{language.upper()} compiler diagnostic: {match.group(4)}",
                    int(match.group(1)),
                    int(match.group(2) or 1),
                    kind.upper().replace(" ", "_"),
                )
            )
        if result.returncode != 0 and not findings:
            message = next((line.strip() for line in output.splitlines() if line.strip()), "Compiler exited with an error")
            findings.append(_finding(language, SeverityEnum.CRITICAL, f"Compiler error: {message}", message, rule_suffix="ERROR"))
    elif language == "javascript":
        line_match = re.search(r"^\[stdin\]:(\d+)$", output, re.MULTILINE)
        caret_line = next((line for line in output.splitlines() if re.match(r"^\s*\^", line)), "")
        message_match = re.search(r"\nSyntaxError: (.+)", output)
        if result.returncode != 0:
            line = int(line_match.group(1)) if line_match else 1
            column = caret_line.find("^") + 1 if caret_line else 1
            message = message_match.group(1) if message_match else "Invalid JavaScript syntax"
            findings.append(
                _finding(
                    language,
                    SeverityEnum.CRITICAL,
                    f"Syntax error: {message}",
                    f"Node.js could not parse the JavaScript at line {line}, column {column}.",
                    line,
                    column,
                    "SYNTAX",
                )
            )
    elif language in ("typescript", "java"):
        if language == "typescript":
            pattern = re.compile(r"^.*?\((\d+),(\d+)\):\s*(error|warning)\s+TS\d+:\s*(.+)$")
        else:
            pattern = re.compile(r"^.*?:(\d+):\s*(error|warning):\s*(.+)$")
        for line in output.splitlines():
            match = pattern.match(line.strip())
            if not match:
                continue
            diagnostic_kind = match.group(3) if language == "typescript" else match.group(2)
            is_error = diagnostic_kind == "error"
            message = match.group(4) if language == "typescript" else match.group(3)
            findings.append(
                _finding(
                    language,
                    SeverityEnum.CRITICAL if is_error else SeverityEnum.MEDIUM,
                    f"{'Error' if is_error else 'Warning'}: {message}",
                    f"{language.upper()} compiler diagnostic: {message}",
                    int(match.group(1)),
                    int(match.group(2)) if language == "typescript" else 1,
                    "ERROR" if is_error else "WARNING",
                )
            )
        if result.returncode != 0 and not findings:
            message = next((line.strip() for line in output.splitlines() if line.strip()), "Compiler exited with an error")
            findings.append(_finding(language, SeverityEnum.CRITICAL, f"Compiler error: {message}", message, rule_suffix="ERROR"))

    return findings[:100], True


def run_compiler_diagnostics(code: str, language: str) -> Tuple[List[FindingSchema], bool]:
    """Return compile-only diagnostics and whether a compiler check completed."""
    if language == "python":
        try:
            compile(code, "<devlens-snippet>", "exec", dont_inherit=True)
            return [], True
        except SyntaxError as error:
            return [
                _finding(
                    language,
                    SeverityEnum.CRITICAL,
                    f"Syntax error: {error.msg}",
                    error.text.strip() if error.text else error.msg,
                    error.lineno or 1,
                    error.offset or 1,
                    "SYNTAX",
                )
            ], True

    if language == "javascript":
        executable = shutil.which("node")
        if not executable:
            return [_unavailable(language, "Node.js is not installed on this backend.")], False
        return _run([executable, "--check", "--input-type=module", "-"], language, code=code)

    if language in ("c", "cpp"):
        include_message = _c_include_safety_message(code)
        if include_message:
            return [_unavailable(language, include_message)], False
        compiler_name = "gcc" if language == "c" else "g++"
        compiler = shutil.which(compiler_name)
        if not compiler:
            return [_unavailable(language, f"The {language.upper()} compiler is not installed on this backend.")], False
        standard = "c17" if language == "c" else "c++20"
        flags = ["-std=" + standard, "-Wall", "-Wextra", "-Wpedantic", "-fsyntax-only", "-x", "c" if language == "c" else "c++"]
        if language == "c":
            flags.append("-Werror=implicit-function-declaration")
        with tempfile.TemporaryDirectory(prefix="devlens-compiler-") as work_directory:
            return _run([compiler, *flags, "-"], language, cwd=work_directory, code=code)

    if language == "typescript":
        compiler = shutil.which("tsc")
        if not compiler:
            return [_unavailable(language, "The TypeScript compiler (tsc) is not installed on this backend.")], False
        with tempfile.TemporaryDirectory(prefix="devlens-typescript-") as work_directory:
            source_path = Path(work_directory) / "snippet.ts"
            source_path.write_text(code, encoding="utf-8")
            command = [compiler, "--noEmit", "--pretty", "false", "--skipLibCheck", "--strict", "--noResolve", "--target", "ES2020", "--module", "ESNext", str(source_path)]
            return _run(command, language, cwd=work_directory)

    if language == "java":
        compiler = shutil.which("javac")
        if not compiler:
            return [_unavailable(language, "The Java compiler (javac) is not installed on this backend.")], False
        public_type = re.search(r"\bpublic\s+(?:class|interface|enum|record)\s+([A-Za-z_]\w*)", code)
        file_name = f"{public_type.group(1) if public_type else 'Snippet'}.java"
        with tempfile.TemporaryDirectory(prefix="devlens-java-") as work_directory:
            source_path = Path(work_directory) / file_name
            source_path.write_text(code, encoding="utf-8")
            command = [compiler, "-Xlint:all", "-proc:none", "-classpath", "", "-sourcepath", "", "-d", work_directory, str(source_path)]
            return _run(command, language, cwd=work_directory)

    return [], False
