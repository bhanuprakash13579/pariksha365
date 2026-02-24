from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user_schema import UserResponse, UserUpdate
from app.schemas.auth_schema import ChangePasswordRequest, MessageResponse
from app.services import auth_service

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

from app.schemas.course_schema import CourseResponse
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

@router.get("/me/enrollments", response_model=List[CourseResponse])
async def read_user_enrollments(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get courses the current user is enrolled in.
    """
    from app.models.enrollment import Enrollment
    from app.models.course import Course
    from app.models.course_folder import CourseFolder
    
    stmt = (
        select(Enrollment)
        .options(
            selectinload(Enrollment.course)
            .selectinload(Course.folders)
            .selectinload(CourseFolder.tests)
        )
        .where(Enrollment.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    enrollments = result.scalars().all()
    return [e.course for e in enrollments if e.course]

@router.put("/me", response_model=UserResponse)
async def update_user_me(
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update current user profile (name, phone).
    """
    return await auth_service.update_user(db, current_user, user_update)

@router.put("/me/password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Change current user's password.
    """
    await auth_service.change_password(db, current_user, body.old_password, body.new_password)
    return MessageResponse(message="Password changed successfully.")
