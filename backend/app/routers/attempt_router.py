from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.attempt_schema import AttemptCreate, AttemptResponse, UserAnswerCreate, UserAnswerResponse
from app.schemas.result_schema import ResultResponse
from app.services import scoring_service

router = APIRouter()

@router.post("/start", response_model=AttemptResponse)
async def start_attempt(
    attempt_in: AttemptCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return await scoring_service.start_attempt(db, current_user.id, attempt_in.test_series_id)

@router.post("/{attempt_id}/answers", response_model=UserAnswerResponse)
async def save_answer(
    attempt_id: uuid.UUID,
    answer_in: UserAnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return await scoring_service.save_answer(db, attempt_id, answer_in)

@router.post("/{attempt_id}/submit", response_model=ResultResponse)
async def submit_attempt(
    attempt_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return await scoring_service.submit_attempt(db, attempt_id)
