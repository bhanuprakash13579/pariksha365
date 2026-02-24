import uuid
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class FolderTest(Base):
    __tablename__ = "folder_tests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("course_folders.id"), index=True)
    test_id = Column(UUID(as_uuid=True), ForeignKey("test_series.id"), index=True)
    order = Column(Integer, default=0)

    folder = relationship("CourseFolder", back_populates="tests")
    test_series = relationship("TestSeries", back_populates="folder_links")
