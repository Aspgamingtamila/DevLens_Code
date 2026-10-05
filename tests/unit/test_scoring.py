"""Unit tests for DevLens Quality Estimate (DQE) scoring."""

from backend.app.schemas.metrics import AnalysisMetricSchema
from backend.app.services.scoring_service import calculate_dqe_score


def test_dqe_perfect_score():
    metrics = AnalysisMetricSchema(
        lines_of_code=25,
        cyclomatic_complexity=2,
        comment_ratio=0.25,
        maintainability_index=95.0,
        correctness_score=100.0,
        security_score=100.0,
        complexity_score=100.0,
        readability_score=95.0,
        testing_score=90.0,
    )
    score, grade = calculate_dqe_score(metrics)
    assert 90.0 <= score <= 100.0
    assert grade == "A"


def test_dqe_critical_security_penalty():
    metrics = AnalysisMetricSchema(
        lines_of_code=100,
        cyclomatic_complexity=15,
        comment_ratio=0.0,
        maintainability_index=40.0,
        correctness_score=40.0,
        security_score=0.0,
        complexity_score=30.0,
        readability_score=40.0,
        testing_score=30.0,
    )
    score, grade = calculate_dqe_score(metrics)
    assert score < 50.0
    assert grade == "F"
