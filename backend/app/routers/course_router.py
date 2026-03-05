from typing import Any, List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import uuid
from app.core.database import get_db
from app.schemas.course_schema import CourseResponse, CourseCreate, CourseFolderResponse, CourseFolderCreate, FolderTestResponse, FolderTestCreate
from app.services import course_service

router = APIRouter()

@router.get("", response_model=List[CourseResponse])
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

@router.post("", response_model=CourseResponse)
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

class OrderUpdateRequest(BaseModel):
    items: List[dict] # Expected format: [{"id": "uuid", "order": int}]

@router.put("/folders/{folder_id}/tests/order")
async def update_folder_tests_order(
    folder_id: uuid.UUID,
    request: OrderUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Bulk update the order of tests within a folder"""
    from sqlalchemy import update
    from app.models.folder_test import FolderTest
    
    for item in request.items:
        stmt = (
            update(FolderTest)
            .where(FolderTest.id == uuid.UUID(item["id"]), FolderTest.folder_id == folder_id)
            .values(order=item["order"])
        )
        await db.execute(stmt)
    await db.commit()
    return {"message": "Order updated successfully"}

@router.put("/{course_id}/folders/order")
async def update_course_folders_order(
    course_id: uuid.UUID,
    request: OrderUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Bulk update the order of folders within a course"""
    from sqlalchemy import update
    from app.models.course_folder import CourseFolder
    
    for item in request.items:
        stmt = (
            update(CourseFolder)
            .where(CourseFolder.id == uuid.UUID(item["id"]), CourseFolder.course_id == course_id)
            .values(order=item["order"])
        )
        await db.execute(stmt)
    await db.commit()
    return {"message": "Order updated successfully"}

from app.core.dependencies import get_current_active_user
from app.models.user import User

@router.post("/{course_id}/enroll")
async def enroll_in_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Enroll current user in a free course. For paid courses, use payment flow.
    """
    return await course_service.enroll_user(db, current_user.id, course_id)

@router.delete("/{course_id}")
async def delete_course(
    course_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a course and all its nested folders/tests.
    """
    return await course_service.delete_course(db, course_id)

@router.delete("/folders/{folder_id}")
async def delete_folder(
    folder_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Delete a folder from a course.
    """
    return await course_service.delete_folder(db, folder_id)

@router.delete("/folders/{folder_id}/tests/{test_id}")
async def unlink_test_from_folder(
    folder_id: uuid.UUID,
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Unlink a test from a folder.
    """
    return await course_service.unlink_test_from_folder(db, folder_id, test_id)
