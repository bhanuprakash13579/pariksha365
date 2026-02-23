from typing import Any
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import stripe
from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.payment_schema import CheckoutSessionResponse
from app.services import payment_service

router = APIRouter()

@router.post("/create-checkout-session/{test_id}", response_model=CheckoutSessionResponse)
async def create_checkout(
    test_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Create a Stripe Checkout Session for Web-first flow.
    """
    url = await payment_service.create_checkout_session(db, current_user.id, test_id)
    return CheckoutSessionResponse(checkout_url=url)

@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> Any:
    """
    Stripe Webhook to verify payment signature and unlock test series securely.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail="Invalid signature")

    await payment_service.handle_stripe_webhook(db, event)
    return {"status": "success"}
