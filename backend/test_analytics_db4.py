import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.database import engine
from app.models.user import User
from app.services import admin_analytics_service

async def main():
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async_session_instance = async_session()
    
    try:
        analytics = await admin_analytics_service.get_system_overview(async_session_instance)
        print("Admin Analytics:")
        print(analytics)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error admin_analytics_service: {e}")
    finally:
        await async_session_instance.close()

if __name__ == "__main__":
    asyncio.run(main())
