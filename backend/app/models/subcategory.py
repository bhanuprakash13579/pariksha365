import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SubCategory(Base):
    """Individual exam within a :class:`Category` — e.g. "SBI PO" under "Banks",
    "CGL" under "SSC", "NTPC" under "RRB".
    """

    __tablename__ = "subcategories"
    __table_args__ = (UniqueConstraint("category_id", "slug", name="uq_subcategory_cat_slug"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, index=True, nullable=False)
    slug = Column(String, nullable=False)  # URL-safe e.g. "sbi-po", "cgl"
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    is_enabled = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("Category", back_populates="subcategories")
    courses = relationship("Course", back_populates="subcategory")
    exam_stages = relationship(
        "ExamStage",
        back_populates="subcategory",
        cascade="all, delete-orphan",
        order_by="ExamStage.order",
    )
