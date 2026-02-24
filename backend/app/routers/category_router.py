from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.schemas import category_schema
from app.services import category_service

router = APIRouter()

@router.get("/", response_model=List[category_schema.Category])
async def read_categories(db: AsyncSession = Depends(get_db)):
    """
    Retrieve all custom active categories and their nested subcategories.
    """
    categories = await category_service.get_all_categories(db)
    return categories
