from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.schemas.course_schema import CourseResponse, CourseCreate, CourseFolderResponse, CourseFolderCreate, FolderTestResponse, FolderTestCreate
from app.services import course_service

router = APIRouter()

@router.get("/", response_model=List[CourseResponse])
async def list_courses(
    subcategory_id: Optional[uuid.UUID] = None,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Retrieve all published courses.
    """
    return await course_service.get_courses(db, subcategory_id=subcategory_id, is_published=True)

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Get detailed view of a course including folders and mapped tests.
    """
    return await course_service.get_course_by_id(db, course_id)

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_in: CourseCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Create a new course. (Admin only ideally, omitting auth for brevity)
    """
    return await course_service.create_course(db, course_in)

@router.post("/{course_id}/folders", response_model=CourseFolderResponse)
async def create_course_folder(
    course_id: uuid.UUID,
    folder_in: CourseFolderCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Add a folder (segment) to a course.
    """
    return await course_service.create_course_folder(db, course_id, folder_in)

@router.post("/folders/{folder_id}/tests", response_model=FolderTestResponse)
async def link_test_to_folder(
    folder_id: uuid.UUID,
    test_in: FolderTestCreate,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Link a TestSeries mock test to a CourseFolder.
    """
    return await course_service.link_test_to_folder(db, folder_id, test_in)
