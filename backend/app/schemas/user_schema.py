from pydantic import BaseModel, EmailStr
from typing import Optional
import uuid
from datetime import datetime

class RoleBase(BaseModel):
    name: str

class RoleCreate(RoleBase):
    pass

class RoleResponse(RoleBase):
    id: uuid.UUID
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    selected_exam_category_id: Optional[uuid.UUID] = None
    points: int = 0
    stars: int = 0

class UserCreate(UserBase):
    password: str
    role_id: Optional[uuid.UUID] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    selected_exam_category_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None

class UserExamPreferenceUpdate(BaseModel):
    selected_exam_category_id: uuid.UUID

class UserResponse(UserBase):
    id: uuid.UUID
    role_id: Optional[uuid.UUID]
    role: Optional[RoleResponse] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
