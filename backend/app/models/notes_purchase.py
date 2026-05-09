import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class NotesPurchase(Base):
    """Lifetime entitlement to the notes bundle for a user.

    One row = one purchase event. Access check: any row for the user = has
    access (no expiry — notes are lifetime). Multiple rows are allowed (e.g.
    re-purchase after refund) and are harmless.

    ``payment_id`` is nullable so admin can grant access without a payment
    record (same pattern as ExamStagePurchase.payment_id).
    """

    __tablename__ = "notes_purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="SET NULL"),
        nullable=True,
    )
    amount_paid_inr = Column(Integer, nullable=False, default=0)
    purchased_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    user = relationship("User")
    payment = relationship("Payment")
