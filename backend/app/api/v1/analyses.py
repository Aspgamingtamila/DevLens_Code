"""Analyses API endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import desc, select
from sqlalchemy.orm import Session, selectinload

from ...auth.dependencies import get_current_user, get_optional_user
from ...database.session import get_db
from ...models.analysis import Analysis
from ...models.finding import Finding
from ...models.metrics import AnalysisMetric
from ...models.generated_test import GeneratedTest
from ...models.user import User
from ...schemas.analysis import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisSummaryResponse,
    GeneratedTestSchema,
)
from ...schemas.findings import FindingSchema, SeverityEnum, CategoryEnum, SourceEnum
from ...schemas.metrics import AnalysisMetricSchema
from ...security.audit_logger import record_audit_event
from ...security.rate_limiter import rate_limit_analyses
from ...services.analysis_orchestrator import execute_code_analysis

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.post("", response_model=AnalysisResponse, dependencies=[Depends(rate_limit_analyses)])
async def create_analysis(
    payload: AnalysisRequest,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Submits source code for dual deterministic static analysis and educational AI synthesis."""
    response = await execute_code_analysis(request=payload, current_user=current_user, db=db)

    if current_user and payload.save_history:
        client_ip = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        record_audit_event(
            db,
            user_id=current_user.id,
            event_type="ANALYSIS_CREATED",
            ip_address=client_ip,
            user_agent=user_agent,
        )

    return response


@router.get("", response_model=List[AnalysisSummaryResponse])
def list_analyses(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves paginated history of analyses for authenticated user."""
    stmt = (
        select(Analysis)
        .options(selectinload(Analysis.findings))
        .where(Analysis.user_id == current_user.id)
        .order_by(desc(Analysis.created_at))
        .limit(limit)
        .offset(offset)
    )
    result = db.execute(stmt)
    records = result.scalars().all()

    summaries = [
        AnalysisSummaryResponse(
            id=a.id,
            title=a.title,
            language=a.language,
            quality_score=a.quality_score,
            findings_count=len(a.findings),
            created_at=a.created_at,
        )
        for a in records
    ]
    return summaries


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: str,
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """
    Retrieves full analysis report by ID.
    Enforces IDOR check: if analysis has user_id, it is restricted to that user.
    """
    stmt = (
        select(Analysis)
        .options(
            selectinload(Analysis.findings),
            selectinload(Analysis.metrics),
            selectinload(Analysis.generated_tests),
        )
        .where(Analysis.id == analysis_id)
    )
    result = db.execute(stmt)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    # IDOR check: user-owned analysis cannot be accessed by other users
    if record.user_id:
        if not current_user or current_user.id != record.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    findings_schema = [
        FindingSchema(
            id=f.id,
            severity=SeverityEnum(f.severity),
            category=CategoryEnum(f.category),
            source=SourceEnum(f.source),
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
        for f in record.findings
    ]

    metrics_schema = None
    if record.metrics:
        m = record.metrics
        metrics_schema = AnalysisMetricSchema(
            lines_of_code=m.lines_of_code,
            cyclomatic_complexity=m.cyclomatic_complexity,
            comment_ratio=m.comment_ratio,
            maintainability_index=m.maintainability_index,
            correctness_score=m.correctness_score,
            security_score=m.security_score,
            complexity_score=m.complexity_score,
            readability_score=m.readability_score,
            testing_score=m.testing_score,
        )

    tests_schema = [
        GeneratedTestSchema(
            id=t.id,
            test_framework=t.test_framework,
            test_code=t.test_code,
            explanation=t.explanation,
            created_at=t.created_at,
        )
        for t in record.generated_tests
    ]

    return AnalysisResponse(
        id=record.id,
        title=record.title,
        language=record.language,
        code_snippet=record.code_snippet,
        quality_score=record.quality_score or 0.0,
        summary=record.summary or "",
        time_complexity=record.time_complexity or "N/A",
        space_complexity=record.space_complexity or "N/A",
        findings=findings_schema,
        metrics=metrics_schema,
        generated_tests=tests_schema,
        created_at=record.created_at,
        is_saved=record.is_saved,
    )


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(
    analysis_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Permanently deletes a specific analysis record owned by the authenticated user."""
    stmt = select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == current_user.id)
    result = db.execute(stmt)
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found.")

    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    record_audit_event(
        db,
        user_id=current_user.id,
        event_type="ANALYSIS_DELETED",
        ip_address=client_ip,
        user_agent=user_agent,
    )

    db.delete(record)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{analysis_id}/export")
def export_analysis(
    analysis_id: str,
    format: str = Query("markdown", pattern="^(markdown|json)$"),
    current_user: Optional[User] = Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Safely exports analysis report as Markdown or raw JSON."""
    analysis = get_analysis(analysis_id=analysis_id, current_user=current_user, db=db)

    if format == "json":
        return analysis.model_dump()

    md_content = f"""# DevLens Code Intelligence Report: {analysis.title}
Generated: {analysis.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}  
Language: **{analysis.language.upper()}**  
DevLens Quality Estimate (DQE): **{analysis.quality_score}/100**  
Estimated Time Complexity: **{analysis.time_complexity}** | Space Complexity: **{analysis.space_complexity}**  

> **Advisory Disclaimer:** DevLens Quality Estimate is an advisory heuristic. AI suggestions are automated recommendations and must be verified by developers before deployment.

---

## Executive Summary
{analysis.summary}

---

## Detected Findings ({len(analysis.findings)})
"""
    for f in analysis.findings:
        md_content += f"""
### [{f.severity.upper()}] {f.title}
- **Category:** {f.category}
- **Source:** [{f.source.upper()}]
- **Lines:** {f.line_start} - {f.line_end}
- **Confidence:** {f.confidence * 100:.0f}%
{f'- **CWE Reference:** {f.cwe_id}' if f.cwe_id else ''}

**Explanation:**  
{f.explanation}

{f'**Remediation Suggestion:**\\n{f.suggestion}' if f.suggestion else ''}
"""

    if analysis.generated_tests:
        md_content += "\n---\n\n## Generated Unit Tests\n"
        for t in analysis.generated_tests:
            md_content += f"""
### Framework: `{t.test_framework}`
```
{t.test_code}
```
"""

    return Response(
        content=md_content,
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=devlens_{analysis_id}.md"},
    )
