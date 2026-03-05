"""
SubjectTaxonomy — Canonical subject→topic hierarchy with deterministic topic codes.
Each entry maps a topic_code (e.g. POL_FR) to its display_name (e.g. "Fundamental Rights")
and parent subject. Used for exact matching between mock tests and quizzes.
"""
import uuid
from sqlalchemy import Column, String, JSON, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base


class SubjectTaxonomy(Base):
    """Defines the canonical subject→topic mapping with deterministic codes."""
    __tablename__ = "subject_taxonomy"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    subject = Column(String, nullable=False, index=True)        # "Polity"
    topic = Column(String, nullable=False, index=True)          # "Fundamental Rights" (display name)
    topic_code = Column(String, nullable=False, unique=True, index=True)  # "POL_FR" — the matching key
    aliases = Column(JSON, nullable=False, default=list)        # ["fundamental rights", "part iii"]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('subject', 'topic', name='uq_subject_topic'),
    )
