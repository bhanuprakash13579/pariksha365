import uuid
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExamStage(Base):
    """A stage of an exam — e.g. "Prelims"/"Mains" under SBI PO, "Tier 1"/"Tier 2"
    under SSC CGL, "CBT 1"/"CBT 2" under RRB NTPC.

    Sits between SubCategory (the exam itself) and TestSeries (an individual paper).
    Each stage carries its own visibility flag so the admin can release stages
    independently (e.g. enable CGL Tier 1 while Tier 2 content is still in review).

    Pricing: ``price_inr`` and ``validity_days`` gate MOCK children only. PYQ
    ``test_series`` under the same stage stay free regardless (enforced in
    entitlement_service, not the schema). price_inr==0 means the stage is free
    — no entitlement row needed.
    """

    __tablename__ = "exam_stages"
    __table_args__ = (
        UniqueConstraint("subcategory_id", "slug", name="uq_exam_stage_subcat_slug"),
        CheckConstraint("price_inr >= 0", name="ck_exam_stage_price_nonneg"),
        CheckConstraint("validity_days >= 1", name="ck_exam_stage_validity_positive"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    subcategory_id = Column(UUID(as_uuid=True), ForeignKey("subcategories.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)  # Human-readable e.g. "Prelims", "Tier 1"
    slug = Column(String, nullable=False)  # URL-safe e.g. "prelims", "tier-1"
    order = Column(Integer, default=0, nullable=False)
    is_enabled = Column(Boolean, default=False, nullable=False, index=True)
    price_inr = Column(Integer, default=0, nullable=False)
    validity_days = Column(Integer, default=365, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    subcategory = relationship("SubCategory", back_populates="exam_stages")
    exam_pattern = relationship(
        "ExamPattern", back_populates="exam_stage", uselist=False, cascade="all, delete-orphan"
    )
    test_series = relationship("TestSeries", back_populates="exam_stage")
    purchases = relationship(
        "ExamStagePurchase", back_populates="exam_stage", cascade="all, delete-orphan"
    )
