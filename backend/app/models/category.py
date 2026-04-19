import uuid
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Category(Base):
    """Top-level grouping of exams — e.g. "Banks", "SSC", "RRB", "UPSC"."""

    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    icon_name = Column(String, nullable=True)  # e.g. "ribbon-outline"
    image_url = Column(String, nullable=True)  # Custom high-res graphic URL for premium cards
    order = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subcategories = relationship(
        "SubCategory",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="SubCategory.order",
    )
