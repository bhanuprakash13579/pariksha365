from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# ---- SubCategory schemas ---------------------------------------------------

class SubCategoryBase(BaseModel):
    name: str
    order: Optional[int] = 0
    slug: Optional[str] = None
    description: Optional[str] = None


class SubCategoryCreate(SubCategoryBase):
    category_id: UUID


class SubCategory(SubCategoryBase):
    id: UUID
    category_id: UUID
    is_enabled: bool = False
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---- Category schemas ------------------------------------------------------

class CategoryBase(BaseModel):
    name: str
    icon_name: Optional[str] = "grid-outline"
    image_url: Optional[str] = None
    order: Optional[int] = 0
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class Category(CategoryBase):
    id: UUID
    is_enabled: bool = False
    created_at: datetime
    subcategories: List[SubCategory] = []
    model_config = ConfigDict(from_attributes=True)
