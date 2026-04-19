"""Per-ExamStage purchase entitlement.

One row == one purchase event. Access is not a simple boolean — it's time-boxed
by ``expires_at``. A user may have multiple rows for the same stage (e.g. a
re-purchase that extends access); the entitlement check in
``entitlement_service.has_active_stage_access`` looks for any row with
``expires_at > NOW()``.

``validity_days_at_purchase`` is frozen at purchase time so that later admin
edits to the stage's ``validity_days`` don't retroactively shorten a student's
already-purchased window. Same principle for ``amount_paid_inr`` — that's the
price at the moment of purchase, not today's price.
"""
import uuid

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class ExamStagePurchase(Base):
    __tablename__ = "exam_stage_purchases"
    __table_args__ = (
        CheckConstraint("amount_paid_inr >= 0", name="ck_purchase_amount_nonneg"),
        CheckConstraint("expires_at > purchased_at", name="ck_purchase_expiry_after"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    exam_stage_id = Column(UUID(as_uuid=True), ForeignKey("exam_stages.id", ondelete="CASCADE"), nullable=False, index=True)
    amount_paid_inr = Column(Integer, nullable=False)
    validity_days_at_purchase = Column(Integer, nullable=False)
    purchased_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="SET NULL"), nullable=True)
    note = Column(String, nullable=True)

    user = relationship("User", back_populates="stage_purchases")
    exam_stage = relationship("ExamStage", back_populates="purchases")
    payment = relationship("Payment")
