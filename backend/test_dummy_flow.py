import asyncio
import sys
import os
import uuid
from datetime import datetime

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from app.models.user import User
from app.schemas.test_schema import TestSeriesBulkCreate, SectionBulkCreate, QuestionBulkCreate, OptionBulkCreate
from app.schemas.question_schema import OptionCreate
from app.services.test_series_service import create_test_series_bulk
from app.services.scoring_service import start_attempt, save_answer, submit_attempt
from app.schemas.attempt_schema import UserAnswerCreate
from app.services.practice_service import upload_quiz_questions, get_weak_topic_quiz
from sqlalchemy import text

async def run_simulation():
    async with SessionLocal() as db:
        print("--- 1. Creating a Dummy User ---")
        user_id = uuid.uuid4()
        dummy_user = User(
            id=user_id,
            email=f"dummy_{user_id}@test.com",
            name="Mock Simulator User",
            password_hash="hashedsecret"
        )
        db.add(dummy_user)
        await db.commit()
        print(f"User created: {user_id}")
        
        print("\n--- 2. Populating the Quiz Pool ---")
        # Add some questions to the quiz pool that we want to retrieve later
        quiz_payload = [
            {
                "question_text": "[Quiz Pool] Which vitamin deficiency causes night blindness?",
                "subject": "Biology", "topic": "Vitamins & Minerals",
                "topic_code": "BIO_VITAMINS", "difficulty": "EASY",
                "options": [{"option_text": "Vitamin A", "is_correct": True}, {"option_text": "Vitamin B", "is_correct": False}]
            },
            {
                "question_text": "[Quiz Pool] Which part of the constitution contains Fundamental Rights?",
                "subject": "Polity", "topic": "Fundamental Rights",
                "topic_code": "POL_FR", "difficulty": "MEDIUM",
                "options": [{"option_text": "Part III", "is_correct": True}, {"option_text": "Part IV", "is_correct": False}]
            }
        ]
        pool_res = await upload_quiz_questions(db, quiz_payload)
        print("Quiz pool seeded:", pool_res)
        
        print("\n--- 3. Uploading a Mock Test ---")
        # Create a mock test with the EXACT SAME topic_codes as the quiz pool
        test_payload = TestSeriesBulkCreate(
            title="Validation Mock Test",
            description="Testing the weak topic engine.",
            category="SSC",
            sections=[
                SectionBulkCreate(
                    title="General Awareness",
                    time_limit_minutes=10,
                    marks_per_question=2,
                    questions=[
                        # Question 1: Biology (User will get this WRONG)
                        QuestionBulkCreate(
                            question_text="[Mock] What is the chemical name of Vitamin C?",
                            subject="Biology", topic="Vitamins & Minerals",
                            topic_code="BIO_VITAMINS", difficulty="EASY",
                            options=[
                                OptionBulkCreate(option_text="Ascorbic Acid", is_correct=True),
                                OptionBulkCreate(option_text="Citric Acid", is_correct=False)
                            ]
                        ),
                        # Question 2: Polity (User will get this RIGHT)
                        QuestionBulkCreate(
                            question_text="[Mock] Article 21 guarantees which fundamental right?",
                            subject="Polity", topic="Fundamental Rights",
                            topic_code="POL_FR", difficulty="EASY",
                            options=[
                                OptionBulkCreate(option_text="Right to Life", is_correct=True),
                                OptionBulkCreate(option_text="Right to Equality", is_correct=False)
                            ]
                        )
                    ]
                )
            ]
        )
        test_series = await create_test_series_bulk(db, test_payload)
        
        print(f"Mock test created: {test_series.id}")
        
        print("\n--- 4. User Starts and Submits the Mock Test ---")
        from app.models.attempt import Attempt
        attempt_obj = Attempt(user_id=user_id, test_series_id=test_series.id)
        db.add(attempt_obj)
        await db.commit()
        attempt_id = attempt_obj.id
        
        from sqlalchemy.future import select
        from sqlalchemy.orm import selectinload
        from app.models.test_series import TestSeries
        from app.models.section import Section
        stmt = select(TestSeries).options(selectinload(TestSeries.sections).selectinload(Section.questions)).where(TestSeries.id == test_series.id)
        res = await db.execute(stmt)
        test_loaded = res.scalars().first()
        questions = test_loaded.sections[0].questions
        q_bio = next(q for q in questions if q.topic_code == "BIO_VITAMINS")
        q_pol = next(q for q in questions if q.topic_code == "POL_FR")
        
        # User answers BIO WRONG (selects option 1 instead of correct option 0)
        await save_answer(db, attempt_id, UserAnswerCreate(
            question_id=q_bio.id,
            selected_option_index=1, 
            time_spent_seconds=10
        ))
        print("User answered Biology question incorrectly.")
        
        # User answers POLITY RIGHT (selects option 0)
        await save_answer(db, attempt_id, UserAnswerCreate(
            question_id=q_pol.id,
            selected_option_index=0, 
            time_spent_seconds=10
        ))
        print("User answered Polity question correctly.")
        
        result = await submit_attempt(db, attempt_id)
        print(f"Mock Test Submitted! Score: {result.total_score}. Accuracy: {result.accuracy_percentage}%")
        
        print("\n--- 5. Triggering the Weak-Topic Quiz Engine ---")
        quiz_recs = await get_weak_topic_quiz(db, user_id, limit=5)
        
        print(f"\nResults of Weak-Topic Recommendations:")
        print(f"Identified Weak Topics: {[wt['topic_code'] for wt in quiz_recs['weak_topics']]}")
        print("Recommended Quiz Questions:")
        for q in quiz_recs["questions"]:
            print(f" - [{q['topic_code']}] {q['question_text']}")
        
        # Clean up dummy test user data
        print("\n--- Cleaning up dummy data ---")
        await db.execute(text(f"DELETE FROM attempts WHERE user_id = '{user_id}';"))
        await db.execute(text(f"DELETE FROM user_weak_topics WHERE user_id = '{user_id}';"))
        await db.execute(text(f"DELETE FROM user_topic_mastery WHERE user_id = '{user_id}';"))
        await db.execute(text(f"DELETE FROM users WHERE id = '{user_id}';"))
        await db.commit()

if __name__ == "__main__":
    asyncio.run(run_simulation())
