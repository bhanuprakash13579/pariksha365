from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.schemas.test_schema import TestSeriesResponse
from app.services import test_series_service

router = APIRouter()

@router.get("/", response_model=List[TestSeriesResponse])
async def list_test_series(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieve all published test series.
    """
    return await test_series_service.get_test_series_list(db, category=category, is_published=True)

@router.get("/{test_id}", response_model=TestSeriesResponse)
async def get_test_series(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get detailed view of a test series.
    """
    return await test_series_service.get_test_series_by_id(db, test_id)
