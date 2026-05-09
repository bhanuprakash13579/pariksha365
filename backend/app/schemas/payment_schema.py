from pydantic import BaseModel
import uuid
from datetime import datetime
from app.models.payment import PaymentStatus, PaymentProvider


class PaymentCreate(BaseModel):
    course_id: uuid.UUID
    amount: float
    provider: PaymentProvider


class PaymentResponse(PaymentCreate):
    id: uuid.UUID
    user_id: uuid.UUID
    status: PaymentStatus
    transaction_id: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class CashfreeOrderResponse(BaseModel):
    checkout_url: str
    cf_order_id: str


class NotesFileInfo(BaseModel):
    id: str
    title: str
    filename: str
    download_url: str


class NotesAccessResponse(BaseModel):
    has_access: bool
    files: list[NotesFileInfo]
