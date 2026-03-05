import sys
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.test_series_service import delete_test_series
from app.schemas.test_schema import TestSeriesCreate
from app.services import test_series_service
import uuid

async def test_deletion_sweep():
    print("Testing Test Deletion & Cloudinary Sweep...")
    async with SessionLocal() as db:
        try:
            # 1. Create a dummy test
            test_in = TestSeriesCreate(
                title="Cloudinary Deletion Test",
                category="Bank",
                price=0,
                is_free=True,
                validity_days=30
            )
            created_test = await test_series_service.create_test_series(db, test_in)
            print("Created dummy test ID:", created_test.id)
            
            # 2. Try deleting it to see if our Regex and Cloudinary sweeper crash
            result = await delete_test_series(db, created_test.id)
            print("Deletion Result:", result)
        except Exception as e:
            print("ERROR during deletion testing:", type(e).__name__, str(e))

if __name__ == "__main__":
    asyncio.run(test_deletion_sweep())
