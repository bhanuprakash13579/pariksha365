import asyncio
import argparse
import sys
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.models.test_series import TestSeries
from app.models.section import Section
from app.models.question import Question
import httpx

# Local DB URL
LOCAL_DB_URL = "sqlite+aiosqlite:///./pariksha365.db"

async def get_test_from_local(test_id_str: str):
    try:
        test_id = uuid.UUID(test_id_str)
    except Exception:
        print("Invalid UUID format.")
        return None

    engine = create_async_engine(LOCAL_DB_URL, echo=False)
    async with AsyncSession(engine) as session:
        result = await session.execute(
            select(TestSeries)
            .options(
                selectinload(TestSeries.sections)
                .selectinload(Section.questions)
                .selectinload(Question.options)
            )
            .filter(TestSeries.id == test_id)
        )
        test = result.scalars().first()
        await engine.dispose()
        return test

def convert_test_to_payload(test: TestSeries):
    """Converts the SQLAlchemy model tree into a dict payload matching TestSeriesBulkCreate."""
    payload = {
        "title": test.title,
        "description": test.description,
        "category": test.category,
        "price": test.price,
        "is_free": test.is_free,
        "validity_days": test.validity_days,
        "negative_marking": test.negative_marking,
        "shuffle_questions": test.shuffle_questions,
        "show_notes": test.show_notes,
        "is_published": test.is_published,
        "sections": []
    }
    
    for section in test.sections:
        sec_payload = {
            "title": section.title,
            "time_limit_minutes": section.time_limit_minutes,
            "marks_per_question": section.marks_per_question,
            "questions": []
        }
        for q in section.questions:
            q_payload = {
                "question_text": q.question_text,
                "image_url": q.image_url,
                "explanation": q.explanation,
                "difficulty": q.difficulty.value if hasattr(q.difficulty, 'value') else q.difficulty,
                "subject": q.subject,
                "topic": q.topic,
                "options": []
            }
            for opt in q.options:
                q_payload["options"].append({
                    "option_text": opt.option_text,
                    "is_correct": opt.is_correct
                })
            sec_payload["questions"].append(q_payload)
        payload["sections"].append(sec_payload)
        
    return payload

async def sync_to_prod(test_id: str, prod_url: str, admin_token: str):
    print(f"Fetching TestSeries {test_id} from local SQLite...")
    test = await get_test_from_local(test_id)
    
    if not test:
        print("Test Series not found locally.")
        return False
        
    num_sections = len(test.sections)
    num_questions = sum(len(s.questions) for s in test.sections)
    
    print("\nLocal Test Found:")
    print(f"  Title: {test.title}")
    print(f"  Sections: {num_sections}")
    print(f"  Total Questions: {num_questions}")
    print(f"  Published: {test.is_published}")
    
    confirm = input(f"\nPush this test '{test.title}' to production? (y/n): ")
    if confirm.lower() != 'y':
        print("Sync cancelled.")
        return False
        
    payload = convert_test_to_payload(test)
    
    # Strip any trailing slashes to prevent //api issues
    prod_url = prod_url.rstrip('/')
    print(f"\nConnecting to Production API: {prod_url}")
    
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            target_endpoint = f"{prod_url}/api/v1/tests/bulk"
            print(f"POST {target_endpoint}...")
            
            response = await client.post(target_endpoint, json=payload, headers=headers, timeout=60.0)
            
            if response.status_code in [200, 201]:
                print("\n✅ Successfully synced to production!")
                data = response.json()
                print(f"New Production Test ID: {data.get('id')}")
                return True
            else:
                print(f"\n❌ Failed to sync. API returned {response.status_code}:")
                print(response.text)
                return False
                
        except Exception as e:
            print(f"\n❌ Connection Error: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description="Sync a local mock test to the production server.")
    parser.add_argument("test_id", help="The UUID of the Test Series in your local database.")
    parser.add_argument("--url", required=True, help="Your production API URL (e.g. https://api.pariksha365.in)")
    parser.add_argument("--token", required=True, help="Your production Admin JWT token.")
    
    args = parser.parse_args()
    success = asyncio.run(sync_to_prod(args.test_id, args.url, args.token))
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()
