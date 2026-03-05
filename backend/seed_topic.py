import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import SessionLocal
from app.services import taxonomy_service

async def main():
    async with SessionLocal() as db:
        await taxonomy_service.create_entry(db, "Geography", "Straits, Bays and Gulfs", "GEO_STRAITS_BAYS", ["straits", "bays", "gulfs"])
        print("Success")

if __name__ == "__main__":
    asyncio.run(main())
