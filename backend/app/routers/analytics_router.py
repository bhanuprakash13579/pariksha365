from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.attempt import Attempt
from app.models.user_answer import UserAnswer
from app.models.question import Question
from app.schemas.analytics_schema import AttemptAnalyticsResponse, SeriesAnalyticsResponse, HierarchyCategory, OverallCourseAnalyticsResponse, SpecificTestAnalyticsResponse
from app.schemas.feedback_schema import FeedbackReport
from typing import List
from app.services import analytics_service, feedback_engine

router = APIRouter()

@router.get("/hierarchy", response_model=List[HierarchyCategory])
async def get_analytics_hierarchy_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the enrolled Category -> Course hierarchy for analytics."""
    return await analytics_service.get_analytics_hierarchy(db, current_user.id)

@router.get("/course/{course_id}/overall", response_model=OverallCourseAnalyticsResponse)
async def get_course_overall_analytics_endpoint(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get aggregated analytics across all attempts in a course."""
    return await analytics_service.get_course_overall_analytics(db, course_id, current_user.id)

@router.get("/course/{course_id}/test/{test_series_id}", response_model=SpecificTestAnalyticsResponse)
async def get_specific_test_analytics_endpoint(
    course_id: uuid.UUID,
    test_series_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get analytics for a specific test attempt within a course context."""
    return await analytics_service.get_specific_test_analytics(db, test_series_id, current_user.id)

@router.get("/attempt/{attempt_id}", response_model=AttemptAnalyticsResponse)
async def get_attempt_analytics_endpoint(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed subject-wise analytics for a specific test attempt.
    """
    return await analytics_service.get_attempt_analytics(db, attempt_id, current_user.id)


@router.get("/attempt/{attempt_id}/feedback", response_model=FeedbackReport)
async def get_attempt_feedback_endpoint(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Personalised post-attempt feedback.

    Returns topic-level breakdowns, section time-budget compliance, and a
    ranked list of actionable recommendations (tier-weighted so Tier A
    quick-wins outrank Tier C drudgery for weak students). See
    :mod:`app.services.feedback_engine` for the scoring rules.
    """
    # Eager-load everything the engine needs to avoid N+1 queries.
    stmt = (
        select(Attempt)
        .where(Attempt.id == attempt_id, Attempt.user_id == current_user.id)
        .options(
            selectinload(Attempt.test_series),
            selectinload(Attempt.user_answers)
            .selectinload(UserAnswer.question)
            .selectinload(Question.section),
        )
    )
    attempt = (await db.execute(stmt)).scalar_one_or_none()
    if attempt is None:
        raise HTTPException(status_code=404, detail="Attempt not found")

    exam_slug = getattr(getattr(attempt.test_series, "exam_stage", None), "subcategory_slug", None) \
        if hasattr(attempt.test_series, "exam_stage") else None
    stage_slug = getattr(getattr(attempt.test_series, "exam_stage", None), "slug", None) \
        if hasattr(attempt.test_series, "exam_stage") else None
    return feedback_engine.build_feedback_report(
        attempt,
        exam_slug=exam_slug,
        stage_slug=stage_slug,
        negative_mark=float(getattr(attempt.test_series, "negative_marking", 0.0) or 0.0),
    )

@router.get("/series/{course_id}", response_model=SeriesAnalyticsResponse)
async def get_series_analytics_endpoint(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get aggregated subject-wise analytics across all tests taken within a course.
    """
    return await analytics_service.get_series_analytics(db, course_id, current_user.id)


@router.get("/attempt/{attempt_id}/results")
async def get_post_test_results_endpoint(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive post-test results with:
    - Score, rank, percentile
    - Subject + topic breakdown
    - Weak/strong topic identification
    - Psychological nudges
    """
    return await analytics_service.get_post_test_results(db, attempt_id, current_user.id)

