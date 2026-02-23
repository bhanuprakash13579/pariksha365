import asyncio
import logging
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.models.user import User
from app.models.role import Role
from app.models.test_series import TestSeries
from app.models.section import Section
from app.models.question import Question, DifficultyLevel
from app.models.option import Option
from app.core.security import get_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def seed_data():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            logger.info("Starting database seed...")
            
            # --- Roles ---
            admin_role = Role(name="admin")
            student_role = Role(name="student")
            session.add_all([admin_role, student_role])
            await session.commit()
            
            # --- Users ---
            admin_user = User(
                name="System Admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role_id=admin_role.id
            )
            student_user = User(
                name="Demo Student",
                email="student@example.com",
                hashed_password=get_password_hash("student123"),
                role_id=student_role.id
            )
            session.add_all([admin_user, student_user])
            await session.commit()
            
            # --- Test Series ---
            test_series = TestSeries(
                title="SSC CGL Tier 1 Full Mock",
                description="Complete mock test for SSC CGL Tier 1 preparation.",
                category="SSC",
                price=149.0,
                validity_days=365,
                is_published=True
            )
            session.add(test_series)
            await session.commit()
            
            # --- Sections ---
            quant_section = Section(test_series_id=test_series.id, title="Quantitative Aptitude", order_index=1)
            english_section = Section(test_series_id=test_series.id, title="English Comprehension", order_index=2)
            session.add_all([quant_section, english_section])
            await session.commit()
            
            # --- Questions & Options ---
            q1 = Question(
                section_id=quant_section.id,
                text="If a sum of money doubles itself in 5 years at simple interest, what is the rate of interest?",
                difficulty=DifficultyLevel.EASY,
                topic="Simple Interest",
                order_index=1
            )
            session.add(q1)
            await session.commit()
            
            opts = [
                Option(question_id=q1.id, text="10%", is_correct=False),
                Option(question_id=q1.id, text="15%", is_correct=False),
                Option(question_id=q1.id, text="20%", is_correct=True),
                Option(question_id=q1.id, text="25%", is_correct=False)
            ]
            session.add_all(opts)
            await session.commit()
            
            logger.info("Seed data generated successfully!")
            
        except Exception as e:
            logger.error(f"Seeding failed: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(seed_data())
