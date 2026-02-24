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

@router.post("/", response_model=category_schema.Category)
async def create_category(category: category_schema.CategoryCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new top-level exam category (e.g. SSC, UPSC) with an optional image_url.
    """
    return await category_service.create_category(db, category)
