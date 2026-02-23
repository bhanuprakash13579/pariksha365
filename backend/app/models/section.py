import uuid
from sqlalchemy import Column, String, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Section(Base):
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    test_series_id = Column(UUID(as_uuid=True), ForeignKey("test_series.id"))
    name = Column(String, nullable=False)
    time_limit_minutes = Column(Integer, nullable=True) # Overall test test time could be used if null
    marks_per_question = Column(Float, default=1.0)

    test_series = relationship("TestSeries", back_populates="sections")
    questions = relationship("Question", back_populates="section", cascade="all, delete-orphan")
