"""
QuizPool — Stores questions for the daily quiz classification system.
Questions are organized by subject tag and served randomly to users daily.
"""
import uuid
from sqlalchemy import Column, String, Text, ForeignKey, DateTime, Integer, Boolean, Float, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuizQuestion(Base):
    """Individual quiz question in the pool, tagged with subject + topic."""
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    question_text = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String, default="MEDIUM")
    subject = Column(String, index=True, nullable=False)  # e.g., "Polity", "Reasoning"
    topic = Column(String, index=True, nullable=True)     # e.g., "Fundamental Rights", "Syllogism"
    topic_code = Column(String, index=True, nullable=True)  # e.g., "POL_FR" — deterministic matching key
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    options = Column(JSON, nullable=False, default=list)

class QuizAttempt(Base):
    """Tracks which quiz questions a user has attempted (for spaced repetition)."""
    __tablename__ = "quiz_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id", ondelete="CASCADE"), index=True)
    was_correct = Column(Boolean, default=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())


class UserWeakTopic(Base):
    """Tracks a user's weak topics (auto-updated after each mock test submission)."""
    __tablename__ = "user_weak_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    topic_code = Column(String, index=True, nullable=True)  # deterministic matching key
    accuracy = Column(Float, default=0.0)   # Current accuracy percentage
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserStreak(Base):
    """Tracks daily practice streak for psychological nudging."""
    __tablename__ = "user_streaks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_active_date = Column(DateTime(timezone=True), nullable=True)
    freeze_available = Column(Boolean, default=True)  # One weekly freeze like Duolingo


class UserTopicMastery(Base):
    """Tracks per-user per-topic mastery for adaptive quiz progression."""
    __tablename__ = "user_topic_mastery"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    topic_code = Column(String, index=True, nullable=True)  # deterministic matching key
    total_available = Column(Integer, default=0)        # Total quiz Qs in this topic
    attempted_count = Column(Integer, default=0)         # Unique questions attempted
    correct_count = Column(Integer, default=0)
    current_accuracy = Column(Float, default=0.0)
    mastery_level = Column(String, default="NEEDS_WORK") # NEEDS_WORK / IMPROVING / PROFICIENT / MASTERED
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)

