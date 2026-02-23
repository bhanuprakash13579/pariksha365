import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

class DifficultyLevel(str, enum.Enum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    section_id = Column(UUID(as_uuid=True), ForeignKey("sections.id"))
    question_text = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    explanation = Column(Text, nullable=True)
    difficulty = Column(SAEnum(DifficultyLevel), default=DifficultyLevel.MEDIUM)
    topic = Column(String, nullable=True)

    section = relationship("Section", back_populates="questions")
    options = relationship("Option", back_populates="question", cascade="all, delete-orphan")
    user_answers = relationship("UserAnswer", back_populates="question")
