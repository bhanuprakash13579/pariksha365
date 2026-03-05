import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.services.taxonomy_service import seed_default_taxonomy
from sqlalchemy import text

async def reseed():
    async with SessionLocal() as db:
        print("Clearing old taxonomy data...")
        await db.execute(text("DELETE FROM subject_taxonomy;"))
        await db.commit()
        
        print("Seeding new expanded taxonomy...")
        result = await seed_default_taxonomy(db)
        print("Seed result:", result)

if __name__ == "__main__":
    asyncio.run(reseed())
