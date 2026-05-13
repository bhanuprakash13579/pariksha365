import uuid
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.schemas import category_schema


async def get_all_categories(db: AsyncSession, *, include_disabled: bool = False):
    """List categories with their subcategories.

    Student callers pass ``include_disabled=False`` (the default) and receive
    only categories whose ``is_enabled`` is True, with disabled subcategories
    filtered out. Admin callers pass ``include_disabled=True`` to see the full
    tree including rows they still need to gate-release.
    """
    stmt = (
        select(Category)
        .options(selectinload(Category.subcategories))
        .order_by(Category.order)
    )
    if not include_disabled:
        stmt = stmt.where(Category.is_enabled.is_(True))
    result = await db.execute(stmt)
    categories = list(result.scalars().all())
    if not include_disabled:
        for cat in categories:
            cat.subcategories = [s for s in cat.subcategories if s.is_enabled]
    return categories


async def get_all_categories_admin(db: AsyncSession):
    """Alias for admin flows — surfaces the full tree including disabled rows."""
    return await get_all_categories(db, include_disabled=True)

async def create_category(db: AsyncSession, category: category_schema.CategoryCreate):
    db_category = Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category

async def create_subcategory(db: AsyncSession, subcategory: category_schema.SubCategoryCreate):
    db_subcategory = SubCategory(**subcategory.model_dump())
    db.add(db_subcategory)
    await db.commit()
    await db.refresh(db_subcategory)
    return db_subcategory


async def delete_category(db: AsyncSession, category_id: uuid.UUID) -> None:
    row = await db.get(Category, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    try:
        await db.delete(row)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete: this category has subcategories with courses linked. Remove all courses first.",
        )


async def rename_category(db: AsyncSession, category_id: uuid.UUID, name: str) -> Category:
    row = await db.get(Category, category_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Category not found")
    row.name = name.strip()
    await db.commit()
    await db.refresh(row)
    return row


async def delete_subcategory(db: AsyncSession, subcategory_id: uuid.UUID) -> None:
    row = await db.get(SubCategory, subcategory_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    try:
        await db.delete(row)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Cannot delete: this subcategory still has courses linked to it. Remove all courses first.",
        )


async def rename_subcategory(db: AsyncSession, subcategory_id: uuid.UUID, name: str) -> SubCategory:
    row = await db.get(SubCategory, subcategory_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    row.name = name.strip()
    await db.commit()
    await db.refresh(row)
    return row
