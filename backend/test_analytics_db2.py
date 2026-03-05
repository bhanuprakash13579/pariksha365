import asyncio
import uuid
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload
from sqlalchemy import select
from app.core.database import engine
from app.models.user import User
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.services import analytics_service

async def main():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as db:
        stmt = select(Enrollment).options(selectinload(Enrollment.course))
        res = await db.execute(stmt)
        enrollments = res.scalars().all()
        print(f"Total Enrollments: {len(enrollments)}")
        for e in enrollments:
            print(f"User: {e.user_id}, Course: {e.course.title if e.course else 'None'}")
            
        print("\nLet's test hierarchy for all enrolled users:")
        user_ids = set(e.user_id for e in enrollments)
        for uid in user_ids:
            h = await analytics_service.get_analytics_hierarchy(db, uid)
            print(f"User {uid} hierarchy: {h}")

if __name__ == "__main__":
    asyncio.run(main())
