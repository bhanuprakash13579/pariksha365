from pydantic import BaseModel
from typing import Optional, List
import uuid
from datetime import datetime
from app.models.attempt import AttemptStatus

class UserAnswerCreate(BaseModel):
    question_id: uuid.UUID
    selected_option_id: Optional[uuid.UUID] = None
    time_spent_seconds: int = 0

class UserAnswerResponse(UserAnswerCreate):
    id: uuid.UUID
    attempt_id: uuid.UUID
    
    class Config:
        from_attributes = True

class AttemptBase(BaseModel):
    test_series_id: uuid.UUID

class AttemptCreate(AttemptBase):
    pass

class AttemptResponse(AttemptBase):
    id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    ended_at: Optional[datetime]
    status: AttemptStatus
    
    class Config:
        from_attributes = True
