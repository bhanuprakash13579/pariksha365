import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class Note(Base):
    __tablename__ = "notes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    test_series_id = Column(UUID(as_uuid=True), ForeignKey("test_series.id"))
    file_url = Column(String, nullable=False)
    is_visible = Column(Boolean, default=True)

    test_series = relationship("TestSeries", back_populates="notes")
