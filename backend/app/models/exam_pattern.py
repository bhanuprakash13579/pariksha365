import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExamPattern(Base):
    """Blueprint that describes how a particular exam stage is structured.

    Total duration, total question count, total marks, negative marking, and
    whether the exam uses sectional timing (candidate locked into each section
    for a fixed window, as in SBI/IBPS PO Prelims). The per-section breakdown
    lives in ``SectionPattern`` rows owned by this pattern.

    Mock-test generation reads this to produce tests that exactly mirror the
    real exam, and the test-taker UI reads it to enforce sectional timers and
    negative marking.
    """

    __tablename__ = "exam_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    exam_stage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exam_stages.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    total_duration_minutes = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    total_marks = Column(Float, nullable=False)
    negative_mark_per_wrong = Column(Float, default=0.0, nullable=False)  # absolute value e.g. 0.25, 0.50, 0.333
    has_sectional_timing = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)  # free-form admin notes (e.g. "PwD candidates get 80 minutes")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    exam_stage = relationship("ExamStage", back_populates="exam_pattern")
    section_patterns = relationship(
        "SectionPattern",
        back_populates="exam_pattern",
        cascade="all, delete-orphan",
        order_by="SectionPattern.order",
    )


class SectionPattern(Base):
    """One section inside an :class:`ExamPattern` — name, subject, question count,
    and (optionally) the per-section time limit when sectional timing is enforced.
    """

    __tablename__ = "section_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    exam_pattern_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exam_patterns.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String, nullable=False)  # e.g. "Quantitative Aptitude"
    subject = Column(String, nullable=False, index=True)  # canonical subject key e.g. "QUANT"
    question_count = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=True)  # null when pattern has no sectional timing
    marks_per_question = Column(Float, default=1.0, nullable=False)
    order = Column(Integer, default=0, nullable=False)

    exam_pattern = relationship("ExamPattern", back_populates="section_patterns")
