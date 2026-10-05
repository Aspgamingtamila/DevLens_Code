"""DevLens Quality Estimate (DQE) Scoring Service.

Computes a transparent, 6-pillar advisory quality score (0 - 100).
"""

from typing import Tuple
from ..schemas.metrics import AnalysisMetricSchema, QualityScoreSchema


def calculate_dqe_score(metrics: AnalysisMetricSchema) -> Tuple[float, str]:
    """
    Calculates weighted DQE composite score across 6 pillars:
    - Correctness (25%)
    - Security (20%)
    - Complexity (15%)
    - Maintainability (15%)
    - Readability (15%)
    - Testing Readiness (10%)
    """
    weighted_score = (
        0.25 * metrics.correctness_score +
        0.20 * metrics.security_score +
        0.15 * metrics.complexity_score +
        0.15 * metrics.maintainability_index +
        0.15 * metrics.readability_score +
        0.10 * metrics.testing_score
    )
    final_score = round(max(0.0, min(100.0, weighted_score)), 1)

    if final_score >= 90.0:
        grade = "A"
    elif final_score >= 75.0:
        grade = "B"
    elif final_score >= 60.0:
        grade = "C"
    elif final_score >= 50.0:
        grade = "D"
    else:
        grade = "F"

    return final_score, grade
