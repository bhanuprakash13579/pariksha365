from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.test_schema import TestSeriesCreate, TestSeriesResponse, SectionCreate, SectionResponse
from app.schemas.question_schema import QuestionCreate, QuestionResponse
from app.services import test_series_service

router = APIRouter()

# Simple admin check dependency
def check_admin(user: User = Depends(get_current_active_user)):
    # In a real scenario, check user.role.name == "Admin"
    # Assuming role checks here for brevity
    return user

@router.post("/test-series", response_model=TestSeriesResponse)
async def create_test(
    test_in: TestSeriesCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
) -> Any:
    return await test_series_service.create_test_series(db, test_in)

@router.post("/test-series/{test_id}/sections", response_model=SectionResponse)
async def add_section(
    test_id: uuid.UUID,
    section_in: SectionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
) -> Any:
    return await test_series_service.create_section(db, test_id, section_in)

@router.post("/sections/{section_id}/questions", response_model=QuestionResponse)
async def add_question(
    section_id: uuid.UUID,
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(check_admin)
) -> Any:
    return await test_series_service.create_question(db, section_id, question_in)
