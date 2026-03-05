from pydantic import BaseModel
from typing import List, Dict, Optional


class TopicPerformance(BaseModel):
    """Performance breakdown for a specific sub-topic within a subject."""
    topic: str
    total_questions: int
    correct: int
    incorrect: int
    skipped: int = 0
    accuracy_percentage: float
    avg_time_seconds: float = 0.0  # Average time per question in this topic
    practice_available: bool = False  # Whether practice questions exist for this topic


class SubjectPerformance(BaseModel):
    subject: str
    total_questions: int
    correct: int
    incorrect: int
    skipped: int
    accuracy_percentage: float
    time_spent_seconds: int
    avg_time_seconds: float = 0.0  # Average time per question
    time_on_correct: int = 0  # Total seconds spent on correctly answered questions
    time_on_incorrect: int = 0  # Total seconds spent on incorrectly answered questions
    time_on_skipped: int = 0  # Total seconds spent on skipped questions (wasted time)
    topics: List[TopicPerformance] = []  # Nested topic breakdown


class AttemptAnalyticsResponse(BaseModel):
    attempt_id: str
    total_score: float
    subject_performances: List[SubjectPerformance]


class SeriesAnalyticsResponse(BaseModel):
    course_id: str
    total_attempts: int
    average_score: float
    subject_performances: List[SubjectPerformance]


class HierarchyCourse(BaseModel):
    course_id: str
    title: str


class HierarchyCategory(BaseModel):
    category_name: str
    courses: List[HierarchyCourse]


class WeakTopicInfo(BaseModel):
    subject: str
    topic: str
    accuracy: float
    total_attempted: int
    practice_question_count: int = 0


class PsychologicalNudge(BaseModel):
    type: str  # loss_aversion, social_proof, progress_anchor, specificity_bias
    message: str
    icon: str = "💡"


class PostTestResultsResponse(BaseModel):
    attempt_id: str
    test_title: str
    total_score: float
    rank: int
    percentile: float
    accuracy: float
    correct_count: int
    incorrect_count: int
    skipped_count: int
    subject_performances: List[SubjectPerformance]
    weak_topics: List[WeakTopicInfo]
    strong_topics: List[WeakTopicInfo] = []
    nudges: List[PsychologicalNudge]
    encouragement: str


class OverallCourseAnalyticsResponse(BaseModel):
    course_id: str
    course_title: str
    overall_accuracy: float
    course_percentile: float
    total_attempts: int
    subject_performances: List[SubjectPerformance]
    insights: List[str]
    available_tests: List[HierarchyCourse]


class SpecificTestAnalyticsResponse(BaseModel):
    test_series_id: str
    test_title: str
    total_score: float
    rank: int
    percentile: float
    accuracy: float
    subject_performances: List[SubjectPerformance]
    insights: List[str]
