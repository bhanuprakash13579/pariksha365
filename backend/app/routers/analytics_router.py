from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics_schema import AttemptAnalyticsResponse, SeriesAnalyticsResponse, HierarchyCategory, OverallCourseAnalyticsResponse, SpecificTestAnalyticsResponse
from typing import List
from app.services import analytics_service

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

