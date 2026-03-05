import asyncio
from app.core.database import async_session_maker
from app.models.category import Category
from app.models.course import Course
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.models.test_series import TestSeries
from app.models.section import Section
from app.models.question import Question, DifficultyLevel
import uuid

async def seed_data():
    async with async_session_maker() as session:
        # Create Category
        cat_id = uuid.uuid4()
        cat = Category(id=cat_id, name="UPSC Civil Services", image_url="https://images.unsplash.com/photo-1546410531-df4cb9d8a3be?w=500&auto=format&fit=crop")
        session.add(cat)
        
        # Create Course
        course_id = uuid.uuid4()
        course = Course(id=course_id, title="UPSC Prelims Masterclass 2026", description="Complete coverage of GS Paper 1 and CSAT.", price=2999, is_published=True, subcategory_id=cat_id)
        session.add(course)
        
        # Create Folder
        folder_id = uuid.uuid4()
        folder = CourseFolder(id=folder_id, course_id=course_id, title="Mock Tests (GS Paper 1)", order=1, is_free=True)
        session.add(folder)
        
        # Create Test Series
        test_id = uuid.uuid4()
        test = TestSeries(id=test_id, category="UPSC", title="UPSC GS1 Full Length Mock 1", description="100 Questions covering History, Polity, Economy, and Geography.", negative_marking=0.33)
        session.add(test)
        
        # Map Test to Folder
        mapping = FolderTest(id=uuid.uuid4(), folder_id=folder_id, test_id=test_id, order=1)
        session.add(mapping)

        # Create Section
        section_id = uuid.uuid4()
        section = Section(id=section_id, test_series_id=test_id, name="General Studies", time_limit_minutes=120, marks_per_question=2.0)
        session.add(section)
        
        # Add Questions to Section
        q1 = Question(id=uuid.uuid4(), section_id=section_id, question_text="Which of the following was the first metal used by man?", difficulty=DifficultyLevel.EASY, subject="History", topic="Ancient History")
        q1.options = [
            {"option_text": "Iron", "is_correct": False},
            {"option_text": "Copper", "is_correct": True},
            {"option_text": "Gold", "is_correct": False},
            {"option_text": "Silver", "is_correct": False}
        ]
        
        q2 = Question(id=uuid.uuid4(), section_id=section_id, question_text="The Constitution of India was adopted on:", difficulty=DifficultyLevel.MEDIUM, subject="Polity", topic="Constitution")
        q2.options = [
            {"option_text": "26 January 1950", "is_correct": False},
            {"option_text": "26 November 1949", "is_correct": True},
            {"option_text": "15 August 1947", "is_correct": False},
            {"option_text": "30 January 1948", "is_correct": False}
        ]

        q3 = Question(id=uuid.uuid4(), section_id=section_id, question_text="Who is known as the Father of the Indian Constitution?", difficulty=DifficultyLevel.EASY, subject="Polity", topic="Constitution")
        q3.options = [
            {"option_text": "Jawaharlal Nehru", "is_correct": False},
            {"option_text": "Mahatma Gandhi", "is_correct": False},
            {"option_text": "B. R. Ambedkar", "is_correct": True},
            {"option_text": "Rajendra Prasad", "is_correct": False}
        ]
        
        session.add_all([q1, q2, q3])
        
        await session.commit()
        print("Successfully seeded database with Category, Course, Folder, and a Mock Test!")

if __name__ == "__main__":
    asyncio.run(seed_data())
