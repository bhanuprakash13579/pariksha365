import asyncio
import uuid
import sys
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.core.database import engine
from app.services import analytics_service
from app.models.user import User

async def main():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as db:
        user_stmt = select(User).limit(1)
        res = await db.execute(user_stmt)
        user = res.scalars().first()
        if not user:
            print("No users found")
            return
        
        print(f"User ID: {user.id}")
        
        try:
            hierarchy = await analytics_service.get_analytics_hierarchy(db, user.id)
            print("Hierarchy =>", hierarchy)
        except Exception as e:
            print("Error get_analytics_hierarchy:", e)
            
        try:
            if hierarchy and hierarchy[0]['courses']:
                course_id = hierarchy[0]['courses'][0]['course_id']
                print(f"Course ID: {course_id}")
                analytics = await analytics_service.get_course_overall_analytics(db, uuid.UUID(course_id), user.id)
                print("Course Overall Analytics =>", analytics)
        except Exception as e:
            print("Error get_course_overall_analytics:", e)

if __name__ == "__main__":
    asyncio.run(main())
