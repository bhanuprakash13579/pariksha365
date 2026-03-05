from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from fastapi import HTTPException
from app.models.course import Course
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.models.test_series import TestSeries
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseFolderCreate, FolderTestCreate

async def create_course(db: AsyncSession, course_in: CourseCreate) -> Course:
    db_course = Course(**course_in.model_dump())
    db.add(db_course)
    await db.commit()
    
    # Re-fetch with relationships eagerly loaded to prevent MissingGreenlet
    stmt = select(Course).options(selectinload(Course.folders)).where(Course.id == db_course.id)
    result = await db.execute(stmt)
    return result.scalars().first()

async def get_courses(db: AsyncSession, subcategory_id: Optional[uuid.UUID] = None, is_published: Optional[bool] = None) -> List[Course]:
    stmt = select(Course).options(
        selectinload(Course.folders)
        .selectinload(CourseFolder.tests)
        .selectinload(FolderTest.test_series)
        .selectinload(TestSeries.sections)
    )
    if subcategory_id:
        stmt = stmt.where(Course.subcategory_id == subcategory_id)
    if is_published is not None:
        stmt = stmt.where(Course.is_published == is_published)
    result = await db.execute(stmt)
    courses = list(result.scalars().all())
    
    for course in courses:
        course.folders.sort(key=lambda f: getattr(f, 'order', 0) or 0)
        for folder in course.folders:
            # Filter out dangling tests (test_series deleted but folder link remains)
            folder.tests = [t for t in folder.tests if t.test_id is not None]
            folder.tests.sort(key=lambda t: getattr(t, 'order', 0) or 0)
            
    return courses

async def get_course_by_id(db: AsyncSession, course_id: uuid.UUID) -> Course:
    stmt = (
        select(Course)
        .options(
            selectinload(Course.folders)
            .selectinload(CourseFolder.tests)
            .selectinload(FolderTest.test_series)
        )
        .where(Course.id == course_id)
    )
    result = await db.execute(stmt)
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    course.folders.sort(key=lambda f: getattr(f, 'order', 0) or 0)
    for folder in course.folders:
        # Filter out dangling tests
        folder.tests = [t for t in folder.tests if t.test_id is not None]
        folder.tests.sort(key=lambda t: getattr(t, 'order', 0) or 0)
        
    return course

async def create_course_folder(db: AsyncSession, course_id: uuid.UUID, folder_in: CourseFolderCreate) -> CourseFolder:
    db_folder = CourseFolder(course_id=course_id, **folder_in.model_dump())
    db.add(db_folder)
    await db.commit()
    # Eagerly load the .tests relationship to prevent MissingGreenlet during serialization
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(CourseFolder).where(CourseFolder.id == db_folder.id).options(selectinload(CourseFolder.tests))
    )
    return result.scalars().first()

async def link_test_to_folder(db: AsyncSession, folder_id: uuid.UUID, test_in: FolderTestCreate) -> FolderTest:
    db_link = FolderTest(folder_id=folder_id, **test_in.model_dump())
    db.add(db_link)
    await db.commit()
    # Eagerly load the .test_series and its .sections relationship to prevent MissingGreenlet during serialization
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(FolderTest).where(FolderTest.id == db_link.id).options(
            selectinload(FolderTest.test_series).selectinload(TestSeries.sections)
        )
    )
    return result.scalars().first()

from app.models.enrollment import Enrollment
from datetime import datetime, timedelta

async def enroll_user(db: AsyncSession, user_id: uuid.UUID, course_id: uuid.UUID) -> dict:
    """Enroll a user in a free course."""
    course = await get_course_by_id(db, course_id)
    
    if course.price and course.price > 0:
        raise HTTPException(status_code=402, detail="This is a paid course. Use the payment flow to purchase.")
    
    # Check if already enrolled
    existing = (await db.execute(
        select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)
    )).scalars().first()
    
    if existing:
        return {"message": "Already enrolled", "enrollment_id": str(existing.id)}
    
    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id,
        valid_until=datetime.utcnow() + timedelta(days=course.validity_days or 365)
    )
    db.add(enrollment)
    await db.commit()
    await db.refresh(enrollment)
    return {"message": "Successfully enrolled!", "enrollment_id": str(enrollment.id)}

async def delete_course(db: AsyncSession, course_id: uuid.UUID) -> dict:
    """Delete a course and all its nested folders/tests."""
    course = (await db.execute(select(Course).where(Course.id == course_id))).scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    await db.delete(course)
    await db.commit()
    return {"message": f"Course '{course.title}' deleted successfully"}

async def delete_folder(db: AsyncSession, folder_id: uuid.UUID) -> dict:
    """Delete a folder and its linked tests."""
    folder = (await db.execute(select(CourseFolder).where(CourseFolder.id == folder_id))).scalars().first()
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    await db.delete(folder)
    await db.commit()
    return {"message": f"Folder '{folder.title}' deleted successfully"}

async def unlink_test_from_folder(db: AsyncSession, folder_id: uuid.UUID, test_id: uuid.UUID) -> dict:
    """Unlink a test from a folder."""
    link = (await db.execute(
        select(FolderTest).where(FolderTest.folder_id == folder_id, FolderTest.test_id == test_id)
    )).scalars().first()
    if not link:
        raise HTTPException(status_code=404, detail="Test link not found in this folder")
    await db.delete(link)
    await db.commit()
    return {"message": "Test unlinked successfully"}
