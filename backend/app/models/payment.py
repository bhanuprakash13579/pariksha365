import uuid
from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class PaymentProvider(str, enum.Enum):
    STRIPE = "STRIPE"
    UPI = "UPI"
    CASHFREE = "CASHFREE"

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

# Stored as String (not SAEnum) so adding new types never needs a Postgres
# ALTER TYPE migration on an existing production database.
PAYMENT_TYPE_COURSE = "COURSE"
PAYMENT_TYPE_EXAM_STAGE = "EXAM_STAGE"
PAYMENT_TYPE_NOTES_BUNDLE = "NOTES_BUNDLE"

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=True, index=True)
    exam_stage_id = Column(UUID(as_uuid=True), ForeignKey("exam_stages.id", ondelete="SET NULL"), nullable=True, index=True)
    payment_type = Column(String, nullable=True, default=PAYMENT_TYPE_COURSE)
    amount = Column(Float, nullable=False)
    provider = Column(SAEnum(PaymentProvider), nullable=False)
    status = Column(SAEnum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String, nullable=True, unique=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="payments")
    course = relationship("Course", back_populates="payments")
