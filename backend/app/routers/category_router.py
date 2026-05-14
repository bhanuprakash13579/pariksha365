import uuid
from fastapi import APIRouter, Body, Depends
from sqlalchemy import update as _sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.user import User
from app.schemas import category_schema
from app.services import category_service

router = APIRouter()

@router.get("", response_model=List[category_schema.Category])
async def read_categories(db: AsyncSession = Depends(get_db)):
    categories = await category_service.get_all_categories(db)
    return categories


@router.get("/admin", response_model=List[category_schema.Category])
async def read_categories_admin(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return await category_service.get_all_categories(db, include_disabled=True)


@router.post("/admin/restore-visibility")
async def restore_admin_visibility(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    res_cat = await db.execute(_sql_update(Category).values(is_enabled=True))
    res_sub = await db.execute(_sql_update(SubCategory).values(is_enabled=True))
    await db.commit()
    return {
        "ok": True,
        "categories_updated": res_cat.rowcount,
        "subcategories_updated": res_sub.rowcount,
        "message": "All categories + subcategories flipped to is_enabled=True.",
    }


@router.post("", response_model=category_schema.Category)
async def create_category(
    category: category_schema.CategoryCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    return await category_service.create_category(db, category)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    await category_service.delete_category(db, category_id)


@router.patch("/{category_id}")
async def rename_category(
    category_id: uuid.UUID,
    name: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    row = await category_service.rename_category(db, category_id, name)
    return {"id": str(row.id), "name": row.name}


@router.post("/subcategories", response_model=category_schema.SubCategory)
async def create_subcategory(
    subcategory: category_schema.SubCategoryCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    return await category_service.create_subcategory(db, subcategory)


@router.delete("/subcategories/{subcategory_id}", status_code=204)
async def delete_subcategory(
    subcategory_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    await category_service.delete_subcategory(db, subcategory_id)


@router.patch("/subcategories/{subcategory_id}")
async def rename_subcategory(
    subcategory_id: uuid.UUID,
    name: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin_user),
):
    row = await category_service.rename_subcategory(db, subcategory_id, name)
    return {"id": str(row.id), "name": row.name}
