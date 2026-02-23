import stripe
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.core.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentProvider
from app.models.test_series import TestSeries
from app.models.enrollment import Enrollment

stripe.api_key = settings.STRIPE_API_KEY

async def create_checkout_session(db: AsyncSession, user_id: uuid.UUID, test_id: uuid.UUID) -> str:
    stmt = select(TestSeries).where(TestSeries.id == test_id)
    result = await db.execute(stmt)
    test_series = result.scalars().first()
    
    if not test_series:
        raise HTTPException(status_code=404, detail="Test series not found")
        
    if test_series.is_free:
        raise HTTPException(status_code=400, detail="Test series is free")
        
    # Create DB Intent payment first
    db_payment = Payment(
        user_id=user_id,
        test_series_id=test_id,
        amount=test_series.price,
        provider=PaymentProvider.STRIPE,
        status=PaymentStatus.PENDING
    )
    db.add(db_payment)
    await db.commit()
    await db.refresh(db_payment)
    
    # Stripe checkout session
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'inr', # or configured currency
                    'product_data': {
                        'name': test_series.title,
                    },
                    'unit_amount': int(test_series.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"http://localhost:3000/payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"http://localhost:3000/payment-cancelled",
            client_reference_id=str(db_payment.id)
        )
        return session.url
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def handle_stripe_webhook(db: AsyncSession, event: dict):
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_id = session.get('client_reference_id')
        
        if payment_id:
            # Update payment status
            stmt = select(Payment).where(Payment.id == payment_id)
            result = await db.execute(stmt)
            payment = result.scalars().first()
            
            if payment and payment.status != PaymentStatus.SUCCESS:
                payment.status = PaymentStatus.SUCCESS
                payment.transaction_id = session.get('payment_intent')
                db.add(payment)
                
                # Grant access via Enrollment
                enrollment = Enrollment(
                    user_id=payment.user_id,
                    test_series_id=payment.test_series_id
                )
                db.add(enrollment)
                await db.commit()
