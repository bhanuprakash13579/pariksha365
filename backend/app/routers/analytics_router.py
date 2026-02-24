from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.analytics_schema import AttemptAnalyticsResponse, SeriesAnalyticsResponse
from app.services import analytics_service

router = APIRouter()

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
