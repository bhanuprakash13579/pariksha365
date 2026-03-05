import asyncio
import json
from app.core.database import async_session_maker
from app.schemas.test_schema import TestSeriesBulkCreate
from app.services.test_series_service import create_test_series_bulk

async def main():
    with open('frontend-web/learntheta_ssc.json', 'r', encoding='utf-8') as f:
        questions = json.load(f)

    payload = {
        "title": "SSC CGL Tier 1 (09 Sep 2024 - Shift 1) [LearnTheta]",
        "category": "SSC CGL Previous Year",
        "is_published": False,
        "sections": [
            {
                "title": "General Section",
                "questions": questions
            }
        ]
    }

    try:
        test_in = TestSeriesBulkCreate(**payload)
        async with async_session_maker() as db:
            await create_test_series_bulk(db, test_in)
            print("Successfully created test series bulk")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
