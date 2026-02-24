import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class TestSeries(Base):
    __tablename__ = "test_series"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String, index=True, nullable=True)
    negative_marking = Column(Float, default=0.25)
    shuffle_questions = Column(Boolean, default=False)
    show_notes = Column(Boolean, default=True)
    can_pause = Column(Boolean, default=False)  # Admin control
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sections = relationship("Section", back_populates="test_series", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="test_series")
    notes = relationship("Note", back_populates="test_series", cascade="all, delete-orphan")
    folder_links = relationship("FolderTest", back_populates="test_series", cascade="all, delete-orphan")
