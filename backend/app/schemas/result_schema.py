from pydantic import BaseModel
from typing import Optional
import uuid

class ResultResponse(BaseModel):
    id: uuid.UUID
    attempt_id: uuid.UUID
    total_score: float
    correct_count: int
    incorrect_count: int
    skipped_count: int
    accuracy_percentage: float
    percentile: Optional[float]
    rank: Optional[int]

    class Config:
        from_attributes = True
