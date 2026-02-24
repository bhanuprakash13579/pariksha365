from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

class FolderTestBase(BaseModel):
    test_id: uuid.UUID
    order: int = 0

class FolderTestCreate(FolderTestBase):
    pass

class FolderTestResponse(FolderTestBase):
    id: uuid.UUID
    folder_id: uuid.UUID
    
    class Config:
        from_attributes = True

class CourseFolderBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_free: bool = False
    order: int = 0

class CourseFolderCreate(CourseFolderBase):
    pass

class CourseFolderResponse(CourseFolderBase):
    id: uuid.UUID
    course_id: uuid.UUID
    tests: List[FolderTestResponse] = []
    
    class Config:
        from_attributes = True

class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    subcategory_id: Optional[uuid.UUID] = None
    thumbnail_url: Optional[str] = None
    price: float = 0.0
    validity_days: int = 365
    is_published: bool = False

class CourseCreate(CourseBase):
    pass

class CourseUpdate(CourseBase):
    title: Optional[str] = None

class CourseResponse(CourseBase):
    id: uuid.UUID
    created_at: datetime
    folders: List[CourseFolderResponse] = []

    class Config:
        from_attributes = True
