from pydantic import BaseModel, root_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# SubCategory Schemas
class SubCategoryBase(BaseModel):
    name: str
    order: Optional[int] = 0

class SubCategoryCreate(SubCategoryBase):
    category_id: UUID

class SubCategory(SubCategoryBase):
    id: UUID
    category_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    icon_name: Optional[str] = "grid-outline"
    order: Optional[int] = 0

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: UUID
    created_at: datetime
    subcategories: List[SubCategory] = []

    class Config:
        from_attributes = True
