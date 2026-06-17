from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.test_schema import TestSeriesResponse, TestSeriesFullResponse, TestSeriesBulkCreate
from app.services import test_series_service

router = APIRouter()

@router.get("", response_model=List[TestSeriesResponse])
async def list_test_series(
    category: Optional[str] = None,
    is_published: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
) -> Any:
    return await test_series_service.get_test_series_list(db, category=category, is_published=is_published)

@router.get("/{test_id}", response_model=TestSeriesFullResponse)
async def get_test_series(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    return await test_series_service.get_test_series_by_id(db, test_id)

@router.post("/bulk", response_model=TestSeriesResponse, status_code=201)
async def upload_test_series_bulk(
    test_data: TestSeriesBulkCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.create_test_series_bulk(db, test_data)

@router.put("/{test_id}", response_model=TestSeriesResponse, status_code=200)
async def update_test_series_full(
    test_id: uuid.UUID,
    test_data: TestSeriesBulkCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.update_test_series_full(db, test_id, test_data)

@router.delete("/{test_id}")
async def delete_test_series(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.delete_test_series(db, test_id)

@router.patch("/{test_id}/publish", response_model=TestSeriesResponse)
async def publish_test_series(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.publish_test_series(db, test_id)
