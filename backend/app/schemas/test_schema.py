from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime

class SectionBase(BaseModel):
    name: str
    time_limit_minutes: Optional[int] = None
    marks_per_question: float = 1.0

class SectionCreate(SectionBase):
    pass

class SectionResponse(SectionBase):
    id: uuid.UUID
    test_series_id: uuid.UUID
    
    class Config:
        from_attributes = True

class TestSeriesBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    price: float = 0.0
    is_free: bool = False
    validity_days: int = 365
    negative_marking: float = 0.25
    shuffle_questions: bool = False
    show_notes: bool = True
    is_published: bool = False
    is_daily_quiz: bool = False
    quiz_date: Optional[datetime] = None

class TestSeriesCreate(TestSeriesBase):
    pass

class TestSeriesUpdate(TestSeriesBase):
    title: Optional[str] = None

class TestSeriesResponse(TestSeriesBase):
    id: uuid.UUID
    created_at: datetime
    sections: List[SectionResponse] = []

    class Config:
        from_attributes = True
