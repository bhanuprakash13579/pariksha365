from pydantic import BaseModel
from typing import Optional, List
import uuid
from app.models.question import DifficultyLevel

class OptionBase(BaseModel):
    option_text: str
    is_correct: bool

class OptionCreate(OptionBase):
    pass

class OptionResponse(OptionBase):
    id: uuid.UUID
    question_id: uuid.UUID

    class Config:
        from_attributes = True

class QuestionBase(BaseModel):
    question_text: str
    image_url: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    topic: Optional[str] = None

class QuestionCreate(QuestionBase):
    options: List[OptionCreate]

class QuestionResponse(QuestionBase):
    id: uuid.UUID
    section_id: uuid.UUID
    options: List[OptionResponse] = []

    class Config:
        from_attributes = True
