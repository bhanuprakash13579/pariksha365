from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.schemas import category_schema

async def get_all_categories(db: AsyncSession):
    # Eager load subcategories so we can return a nested JSON hierarchy
    stmt = select(Category).options(selectinload(Category.subcategories)).order_by(Category.order)
    result = await db.execute(stmt)
    return result.scalars().all()

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
