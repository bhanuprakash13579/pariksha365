import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    test_series_id = Column(UUID(as_uuid=True), ForeignKey("test_series.id"), index=True)
    valid_until = Column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="enrollments")
    test_series = relationship("TestSeries", back_populates="enrollments")
