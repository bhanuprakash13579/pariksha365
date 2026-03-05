from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List, Any

from app.core.database import get_db
from app.services import search_service

router = APIRouter()

@router.get("", response_model=Dict[str, List[Any]])
async def global_search_endpoint(
    q: str = Query(..., min_length=2, description="The search query string"),
    db: AsyncSession = Depends(get_db)
):
    return await search_service.global_search(db, q)
