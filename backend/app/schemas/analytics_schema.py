from pydantic import BaseModel
from typing import List, Dict

class SubjectPerformance(BaseModel):
    subject: str
    total_questions: int
    correct: int
    incorrect: int
    skipped: int
    accuracy_percentage: float
    time_spent_seconds: int

class AttemptAnalyticsResponse(BaseModel):
    attempt_id: str
    total_score: float
    subject_performances: List[SubjectPerformance]

class SeriesAnalyticsResponse(BaseModel):
    course_id: str
    total_attempts: int
    average_score: float
    subject_performances: List[SubjectPerformance]
