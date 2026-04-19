import enum
import uuid
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TestType(str, enum.Enum):
    """Distinguishes generated mock tests from archived previous-year papers."""

    MOCK = "MOCK"
    PYQ = "PYQ"


class TestSeries(Base):
    __tablename__ = "test_series"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=True)  # legacy free-form category label
    negative_marking = Column(Float, default=0.25)
    shuffle_questions = Column(Boolean, default=False)
    show_notes = Column(Boolean, default=True)
    can_pause = Column(Boolean, default=False)
    is_published = Column(Boolean, default=False)
    is_daily_quiz = Column(Boolean, default=False, index=True)
    quiz_date = Column(DateTime(timezone=True), nullable=True, index=True)
    cdn_url = Column(String, nullable=True)  # Cloudflare R2 Global CDN URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Exam-structure linkage (nullable for backward compat with legacy test series)
    exam_stage_id = Column(
        UUID(as_uuid=True),
        ForeignKey("exam_stages.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    test_type = Column(
        SAEnum(TestType, name="test_type_enum"),
        default=TestType.MOCK,
        nullable=False,
        index=True,
    )

    # Provenance for PYQ-type tests (nullable for MOCK)
    source_pdf_path = Column(String, nullable=True)  # absolute or relative path in the corpus
    paper_date = Column(Date, nullable=True)  # date of original exam (best-effort from filename)
    paper_shift = Column(String, nullable=True)  # e.g. "Shift 1", "2nd Shift"

    exam_stage = relationship("ExamStage", back_populates="test_series")
    sections = relationship(
        "Section",
        back_populates="test_series",
        cascade="all, delete-orphan",
        order_by="Section.order_num",
    )
    attempts = relationship("Attempt", back_populates="test_series")
    notes = relationship("Note", back_populates="test_series", cascade="all, delete-orphan")
    folder_links = relationship(
        "FolderTest", back_populates="test_series", cascade="save-update, merge"
    )
