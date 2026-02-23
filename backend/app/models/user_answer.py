import uuid
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    attempt_id = Column(UUID(as_uuid=True), ForeignKey("attempts.id"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"))
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"), nullable=True)
    time_spent_seconds = Column(Integer, default=0)

    attempt = relationship("Attempt", back_populates="user_answers")
    question = relationship("Question", back_populates="user_answers")
    selected_option = relationship("Option", back_populates="user_answers_selected")
