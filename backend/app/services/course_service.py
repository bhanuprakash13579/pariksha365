from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from fastapi import HTTPException
from app.models.course import Course
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.schemas.course_schema import CourseCreate, CourseUpdate, CourseFolderCreate, FolderTestCreate

async def create_course(db: AsyncSession, course_in: CourseCreate) -> Course:
    db_course = Course(**course_in.model_dump())
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course

async def get_courses(db: AsyncSession, subcategory_id: Optional[uuid.UUID] = None, is_published: Optional[bool] = None) -> List[Course]:
    stmt = select(Course)
    if subcategory_id:
        stmt = stmt.where(Course.subcategory_id == subcategory_id)
    if is_published is not None:
        stmt = stmt.where(Course.is_published == is_published)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_course_by_id(db: AsyncSession, course_id: uuid.UUID) -> Course:
    stmt = (
        select(Course)
        .options(selectinload(Course.folders).selectinload(CourseFolder.tests))
        .where(Course.id == course_id)
    )
    result = await db.execute(stmt)
    course = result.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

async def create_course_folder(db: AsyncSession, course_id: uuid.UUID, folder_in: CourseFolderCreate) -> CourseFolder:
    db_folder = CourseFolder(course_id=course_id, **folder_in.model_dump())
    db.add(db_folder)
    await db.commit()
    await db.refresh(db_folder)
    return db_folder

async def link_test_to_folder(db: AsyncSession, folder_id: uuid.UUID, test_in: FolderTestCreate) -> FolderTest:
    db_link = FolderTest(folder_id=folder_id, **test_in.model_dump())
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link
