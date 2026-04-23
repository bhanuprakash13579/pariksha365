"""Private question modules — self-contained question universes gated to specific
user emails. The first such module is the EPFO APFC bank.

Each module has its own questions, its own per-user attempt log, and its own
weak-topic tracker so that signals never leak into the main quiz pool.
"""
import uuid
from sqlalchemy import (
    Column, String, Text, ForeignKey, Integer, Boolean, DateTime, Float, JSON,
    UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class PrivateModule(Base):
    """One row per gated question bank (EPFO APFC, etc.)."""
    __tablename__ = "private_modules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    slug = Column(String, unique=True, nullable=False, index=True)  # e.g. "epfo-apfc"
    name = Column(String, nullable=False)                            # "EPFO APFC MCQ Bank"
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    questions = relationship("PrivateModuleQuestion", back_populates="module",
                             cascade="all, delete-orphan")
    access = relationship("PrivateModuleAccess", back_populates="module",
                          cascade="all, delete-orphan")


class PrivateModuleQuestion(Base):
    __tablename__ = "private_module_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("private_modules.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    qnum = Column(Integer, nullable=True)                  # original PDF question number
    section = Column(String, nullable=True)                # e.g. "II.5 Contributions"
    subject = Column(String, nullable=False, index=True)   # "EPF Act 1952"
    topic = Column(String, nullable=False, index=True)     # "Contributions & Admin Charges"
    topic_code = Column(String, nullable=False, index=True)  # "EPFO_EPF_CONTRIBUTIONS_ADMIN_CHARGES"
    difficulty = Column(String, nullable=False, default="MEDIUM")
    question_text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False, default=list)   # [{option_text, is_correct}, ...]
    explanation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("PrivateModule", back_populates="questions")

    __table_args__ = (
        Index("ix_priv_mod_q_module_subject_topic", "module_id", "subject", "topic_code"),
    )


class PrivateModuleAccess(Base):
    """Email whitelist — one row per (module, email)."""
    __tablename__ = "private_module_access"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("private_modules.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    email = Column(String, nullable=False, index=True)  # normalised to lowercase
    note = Column(String, nullable=True)                # optional admin note
    granted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())

    module = relationship("PrivateModule", back_populates="access")

    __table_args__ = (
        UniqueConstraint("module_id", "email", name="uq_private_module_access_module_email"),
    )


class PrivateModuleAttempt(Base):
    """One row per user answer to a private-module question (used for dedup + weak-topic signal)."""
    __tablename__ = "private_module_attempts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("private_modules.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    question_id = Column(UUID(as_uuid=True),
                         ForeignKey("private_module_questions.id", ondelete="CASCADE"),
                         nullable=False, index=True)
    was_correct = Column(Boolean, nullable=False, default=False)
    attempted_at = Column(DateTime(timezone=True), server_default=func.now())


class PrivateModuleWeakTopic(Base):
    """Module-scoped weak-topic tracker. Kept separate from the main UserWeakTopic so
    that EPFO performance never suggests non-EPFO questions and vice-versa."""
    __tablename__ = "private_module_weak_topics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    module_id = Column(UUID(as_uuid=True), ForeignKey("private_modules.id", ondelete="CASCADE"),
                       nullable=False, index=True)
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=True)
    topic_code = Column(String, nullable=False, index=True)
    accuracy = Column(Float, nullable=False, default=0.0)
    total_questions = Column(Integer, nullable=False, default=0)
    correct_count = Column(Integer, nullable=False, default=0)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "module_id", "topic_code",
                         name="uq_private_module_weak_user_mod_code"),
    )
