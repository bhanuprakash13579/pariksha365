from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from typing import List, Dict, Any

from app.models.category import Category
from app.models.course import Course
from app.models.test_series import TestSeries

async def global_search(db: AsyncSession, query: str) -> Dict[str, List[Any]]:
    if not query or len(query.strip()) < 2:
        return {"categories": [], "courses": [], "tests": []}
    
    search_term = f"%{query.strip()}%"

    # Search Categories
    cat_stmt = select(Category).where(Category.name.ilike(search_term)).limit(5)
    cat_res = await db.execute(cat_stmt)
    categories = [{"id": str(c.id), "name": c.name, "type": "category"} for c in cat_res.scalars().all()]

    # Search Courses
    course_stmt = select(Course).where(Course.title.ilike(search_term), Course.is_published == True).limit(10)
    course_res = await db.execute(course_stmt)
    courses = [{"id": str(c.id), "title": c.title, "type": "course"} for c in course_res.scalars().all()]

    # Search Test Series
    test_stmt = select(TestSeries).where(TestSeries.title.ilike(search_term), TestSeries.is_published == True).limit(10)
    test_res = await db.execute(test_stmt)
    tests = [{"id": str(t.id), "title": t.title, "type": "test"} for t in test_res.scalars().all()]

    return {
        "categories": categories,
        "courses": courses,
        "tests": tests
    }
