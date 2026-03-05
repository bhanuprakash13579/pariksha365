import asyncio
import sys
import os

# Set up the environment to import from the backend
sys.path.insert(0, os.path.join(os.getcwd(), 'backend'))

from app.core.database import SessionLocal
from app.services.taxonomy_service import seed_default_taxonomy
from sqlalchemy import text

async def reseed():
    async with SessionLocal() as db:
        print("Clearing old taxonomy data...")
        await db.execute(text("TRUNCATE TABLE subject_taxonomy CASCADE;"))
        await db.commit()
        
        print("Seeding new expanded taxonomy...")
        result = await seed_default_taxonomy(db)
        print("Seed result:", result)

if __name__ == "__main__":
    asyncio.run(reseed())
