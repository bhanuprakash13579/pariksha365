import asyncio
import os
import sys

# Add backend directory to sys.path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import async_session_maker
from app.services.test_series_service import get_test_series_list

async def main():
    async with async_session_maker() as db:
        tests = await get_test_series_list(db, is_published=False)
        print("Total Drafts:", len(tests))
        for t in tests:
            print(f"- {t.title} | is_published={t.is_published}")

if __name__ == "__main__":
    asyncio.run(main())
