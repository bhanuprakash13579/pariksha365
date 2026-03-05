import asyncio
import sys
import os

sys.path.append(os.getcwd())

from app.core.database import SessionLocal
from sqlalchemy import text

async def alter_db():
    async with SessionLocal() as db:
        print("Adding topic_code to quiz_questions...")
        try:
            await db.execute(text("ALTER TABLE quiz_questions ADD COLUMN topic_code VARCHAR;"))
            await db.execute(text("CREATE INDEX ix_quiz_questions_topic_code ON quiz_questions (topic_code);"))
        except Exception as e:
            print(f"quiz_questions info: {e}")

        print("Adding topic_code to user_weak_topics...")
        try:
            await db.execute(text("ALTER TABLE user_weak_topics ADD COLUMN topic_code VARCHAR;"))
            await db.execute(text("CREATE INDEX ix_user_weak_topics_topic_code ON user_weak_topics (topic_code);"))
        except Exception as e:
            print(f"user_weak_topics info: {e}")

        print("Adding topic_code to user_topic_mastery...")
        try:
            await db.execute(text("ALTER TABLE user_topic_mastery ADD COLUMN topic_code VARCHAR;"))
        except Exception as e:
            print(f"user_topic_mastery info: {e}")
            
        print("Adding topic_code to questions...")
        try:
            await db.execute(text("ALTER TABLE questions ADD COLUMN topic_code VARCHAR;"))
        except Exception as e:
            print(f"questions info: {e}")

        await db.commit()
        print("Database alterations applied.")

if __name__ == "__main__":
    asyncio.run(alter_db())
