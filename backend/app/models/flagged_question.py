"""User-flagged questions — saved questions across all question sources.

Users can flag any question during quiz/mock analysis for later review.
Supports questions from quiz_questions, private_module_questions, and PYQ.
"""
import uuid
from sqlalchemy import (
    Column, String, Text, ForeignKey, DateTime, UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class UserFlaggedQuestion(Base):
    """One row per (user, question_source, question_id) flag.

    question_source values:
        'quiz'           — quiz_questions table (UUID)
        'private_module' — private_module_questions table (UUID)
        'pyq'            — quiz_questions table sourced from PYQ (same table, different source)

    question_id is stored as string UUID so we can work across multiple tables
    without FK constraints (each source table is looked up at query time).
    """
    __tablename__ = "user_flagged_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"),
                     nullable=False, index=True)

    question_source = Column(String(32), nullable=False)   # 'quiz' | 'private_module'
    question_id = Column(String(36), nullable=False)       # UUID as string, no FK

    user_note = Column(Text, nullable=True)                # optional user label/note
    flagged_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "question_source", "question_id",
                         name="uq_flagged_user_source_question"),
        Index("ix_flagged_user_source", "user_id", "question_source"),
    )
