import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.services import analytics_service

async def main():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async_session_instance = async_session()
    
    uid = uuid.UUID("b7ed09f2-e8da-4b69-873e-88339ba495f1")
    cid = uuid.UUID("2fe7afb6-757f-463a-8164-e0fcfdec8a1d")
    
    try:
        analytics = await analytics_service.get_course_overall_analytics(async_session_instance, cid, uid)
        print("Course Overall Analytics:")
        print(analytics)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")
    finally:
        await async_session_instance.close()

if __name__ == "__main__":
    asyncio.run(main())
