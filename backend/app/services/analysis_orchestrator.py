"""Analysis Pipeline Orchestrator.

Combines deterministic static analysis, complexity metrics, AI synthesis,
DQE scoring, and unit test generation into a unified workflow.
"""

import hashlib
import uuid
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from ..analyzers.registry import analyzer_registry
from ..ai.factory import get_ai_provider
from ..logging import logger
from ..models.analysis import Analysis
from ..models.finding import Finding
from ..models.metrics import AnalysisMetric
from ..models.generated_test import GeneratedTest
from ..models.user import User
from ..schemas.analysis import AnalysisRequest, AnalysisResponse, GeneratedTestSchema
from ..schemas.findings import FindingSchema, SourceEnum
from ..security.sanitization import sanitize_code_input
from .scoring_service import calculate_dqe_score
from .testgen_service import generate_tests_for_code


def compute_code_hash(code: str, language: str) -> str:
    """Computes SHA-256 hash for code caching and deduplication."""
    return hashlib.sha256(f"{language.lower()}:{code.strip()}".encode("utf-8")).hexdigest()


async def execute_code_analysis(
    request: AnalysisRequest,
    current_user: Optional[User],
    db: Session,
) -> AnalysisResponse:
    """Executes the complete DevLens analysis pipeline."""
    # 1. Sanitize & validate code
    clean_code, _ = sanitize_code_input(request.code)
    code_hash = compute_code_hash(clean_code, request.language)

    # 2. Run deterministic static analyzer
    analyzer = analyzer_registry.get(request.language)
    static_findings, metrics, time_complexity, space_complexity = analyzer.analyze(clean_code)

    # 3. Call AI provider for synthesis and explanations
    ai_provider = get_ai_provider()
    try:
        ai_output = await ai_provider.analyze_code(
            code=clean_code,
            language=request.language,
            static_findings=static_findings,
        )
    except Exception as e:
        logger.error(f"AI provider failed: {e}. Proceeding with deterministic static findings.")
        ai_output = None

    # 4. Combine and tag findings
    combined_findings: list[FindingSchema] = []
    # Mark static findings
    for f in static_findings:
        f.source = SourceEnum.STATIC
        combined_findings.append(f)

    # Add AI findings with clear AI provenance
    if ai_output and ai_output.findings:
        for aif in ai_output.findings:
            combined_findings.append(
                FindingSchema(
                    severity=aif.severity,
                    category=aif.category,
                    source=SourceEnum.AI,
                    title=aif.title,
                    explanation=aif.explanation,
                    suggestion=aif.suggestion,
                    line_start=aif.line_start,
                    line_end=aif.line_end,
                    confidence=aif.confidence,
                )
            )

    # 5. Calculate DevLens Quality Estimate (DQE)
    quality_score, grade = calculate_dqe_score(metrics)

    # 6. Generate Unit Tests
    generated_tests = generate_tests_for_code(clean_code, request.language)
    if ai_output and ai_output.suggested_tests:
        for t in ai_output.suggested_tests:
            generated_tests.append(
                GeneratedTestSchema(
                    test_framework=t.test_framework,
                    test_code=t.test_code,
                    explanation=t.explanation,
                )
            )

    summary_text = (
        ai_output.summary
        if ai_output
        else f"Analysis completed: {len(combined_findings)} issue(s) detected across {metrics.lines_of_code} lines of code."
    )

    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)
    is_saved = bool(current_user and request.save_history)

    # 7. Persist to database if saving is enabled
    if is_saved:
        db_analysis = Analysis(
            id=analysis_id,
            user_id=current_user.id if current_user else None,
            title=request.title or f"{request.language.upper()} Routine",
            language=request.language,
            code_snippet=clean_code,
            code_hash=code_hash,
            quality_score=quality_score,
            summary=summary_text,
            time_complexity=time_complexity,
            space_complexity=space_complexity,
            created_at=created_at,
            is_saved=True,
        )
        db.add(db_analysis)

        for f in combined_findings:
            db_finding = Finding(
                id=str(uuid.uuid4()),
                analysis_id=analysis_id,
                severity=f.severity.value,
                category=f.category.value,
                source=f.source.value,
                title=f.title,
                explanation=f.explanation,
                suggestion=f.suggestion,
                line_start=f.line_start,
                line_end=f.line_end,
                column_start=f.column_start,
                column_end=f.column_end,
                rule_id=f.rule_id,
                cwe_id=f.cwe_id,
                confidence=f.confidence,
            )
            db.add(db_finding)

        db_metrics = AnalysisMetric(
            id=str(uuid.uuid4()),
            analysis_id=analysis_id,
            lines_of_code=metrics.lines_of_code,
            cyclomatic_complexity=metrics.cyclomatic_complexity,
            comment_ratio=metrics.comment_ratio,
            maintainability_index=metrics.maintainability_index,
            correctness_score=metrics.correctness_score,
            security_score=metrics.security_score,
            complexity_score=metrics.complexity_score,
            readability_score=metrics.readability_score,
            testing_score=metrics.testing_score,
        )
        db.add(db_metrics)

        for gt in generated_tests:
            db_test = GeneratedTest(
                id=str(uuid.uuid4()),
                analysis_id=analysis_id,
                test_framework=gt.test_framework,
                test_code=gt.test_code,
                explanation=gt.explanation,
                created_at=created_at,
            )
            db.add(db_test)

        db.commit()

    return AnalysisResponse(
        id=analysis_id,
        title=request.title or f"{request.language.upper()} Routine",
        language=request.language,
        code_snippet=clean_code,
        quality_score=quality_score,
        summary=summary_text,
        time_complexity=time_complexity,
        space_complexity=space_complexity,
        findings=combined_findings,
        metrics=metrics,
        generated_tests=generated_tests,
        created_at=created_at,
        is_saved=is_saved,
    )
