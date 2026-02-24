import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    # category = Column(String, index=True, nullable=True) # Replaced with dynamic SubCategory
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id"), nullable=True)
    thumbnail_url = Column(String, nullable=True)
    price = Column(Float, default=0.0)
    validity_days = Column(Integer, default=365)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    subcategory = relationship("SubCategory", back_populates="courses")
    folders = relationship("CourseFolder", back_populates="course", cascade="all, delete-orphan", order_by="CourseFolder.order")
    enrollments = relationship("Enrollment", back_populates="course")
    payments = relationship("Payment", back_populates="course")
