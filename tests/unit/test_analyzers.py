"""Unit tests for language deterministic static analyzers."""

import pytest
from backend.app.analyzers.registry import analyzer_registry
from backend.app.schemas.findings import SeverityEnum, CategoryEnum


def test_python_clean_code():
    code = """
def calculate_area(width: float, height: float) -> float:
    # Computes area of a rectangle
    if width <= 0 or height <= 0:
        raise ValueError("Dimensions must be positive")
    return width * height
"""
    analyzer = analyzer_registry.get("python")
    findings, metrics, time_comp, space_comp = analyzer.analyze(code)

    assert metrics.lines_of_code > 0
    assert metrics.cyclomatic_complexity >= 1
    assert time_comp == "O(1)"
    assert space_comp == "O(1)"
    assert not any(f.severity == SeverityEnum.CRITICAL for f in findings)


def test_python_syntax_error():
    code = "def broken_syntax(:\n    return 42"
    analyzer = analyzer_registry.get("python")
    findings, metrics, _, _ = analyzer.analyze(code)

    assert any(f.rule_id == "PY-SYNTAX-001" for f in findings)
    assert any(f.severity == SeverityEnum.CRITICAL for f in findings)


def test_python_dangerous_eval_and_shell():
    code = """
import subprocess

def run_user_cmd(user_input):
    eval(user_input)
    subprocess.Popen(user_input, shell=True)
"""
    analyzer = analyzer_registry.get("python")
    findings, _, _, _ = analyzer.analyze(code)

    eval_finding = next((f for f in findings if f.rule_id == "PY-SEC-001"), None)
    shell_finding = next((f for f in findings if f.rule_id == "PY-SEC-002"), None)

    assert eval_finding is not None
    assert eval_finding.severity == SeverityEnum.CRITICAL
    assert eval_finding.cwe_id == "CWE-95"

    assert shell_finding is not None
    assert shell_finding.severity == SeverityEnum.CRITICAL
    assert shell_finding.cwe_id == "CWE-78"


def test_python_sql_injection_and_nested_loops():
    code = """
def query_and_process(user_id, matrix):
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    for row in matrix:
        for val in row:
            print(val)
"""
    analyzer = analyzer_registry.get("python")
    findings, metrics, time_comp, _ = analyzer.analyze(code)

    sqli = next((f for f in findings if f.cwe_id == "CWE-89"), None)
    assert sqli is not None
    assert sqli.severity == SeverityEnum.CRITICAL

    nested_loop = next((f for f in findings if f.rule_id == "PY-PERF-001"), None)
    assert nested_loop is not None
    assert time_comp == "O(N^2)"


def test_javascript_analyzer_security_and_style():
    code = """
function processData(userInput, items) {
    eval(userInput);
    document.getElementById("output").innerHTML = userInput;
    if (userInput == 0) {
        console.log("zero");
    }
}
"""
    analyzer = analyzer_registry.get("javascript")
    findings, metrics, _, _ = analyzer.analyze(code)

    assert any(f.rule_id == "JS-SEC-001" for f in findings)  # eval
    assert any(f.rule_id == "JS-SEC-002" for f in findings)  # innerHTML
    assert any(f.rule_id == "JS-BUG-001" for f in findings)  # loose equality


def test_cpp_analyzer_unsafe_buffer_operations():
    code = """
#include <stdio.h>
#include <string.h>

void read_input(char *userInput) {
    char buffer[64];
    gets(buffer);
    strcpy(buffer, userInput);
    printf(userInput);
}
"""
    analyzer = analyzer_registry.get("cpp")
    findings, metrics, _, _ = analyzer.analyze(code)

    assert any(f.rule_id == "CPP-SEC-001" for f in findings)  # gets
    assert any(f.rule_id == "CPP-SEC-002" for f in findings)  # strcpy
    assert any(f.rule_id == "CPP-SEC-003" for f in findings)  # printf format string


def test_java_analyzer_sql_injection_and_exceptions():
    code = """
import java.sql.*;

public class UserService {
    public void findUser(Statement stmt, String userId) throws SQLException {
        try {
            stmt.executeQuery("SELECT * FROM users WHERE id = '" + userId + "'");
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
"""
    analyzer = analyzer_registry.get("java")
    findings, metrics, _, _ = analyzer.analyze(code)

    assert any(f.rule_id == "JAVA-SEC-001" for f in findings)  # SQLi
    assert any(f.rule_id == "JAVA-SEC-002" for f in findings)  # printStackTrace
    assert any(f.rule_id == "JAVA-BUG-001" for f in findings)  # Generic catch
