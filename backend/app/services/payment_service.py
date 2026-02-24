import stripe
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from app.core.config import settings
from app.models.payment import Payment, PaymentStatus, PaymentProvider
from app.models.course import Course
from app.models.enrollment import Enrollment

stripe.api_key = settings.STRIPE_API_KEY

async def create_checkout_session(db: AsyncSession, user_id: uuid.UUID, course_id: uuid.UUID) -> str:
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    course = result.scalars().first()
    
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    if course.price <= 0:
        raise HTTPException(status_code=400, detail="Course is free, no payment needed")
        
    # Create DB Intent payment first
    db_payment = Payment(
        user_id=user_id,
        course_id=course_id,
        amount=course.price,
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
                        'name': course.title,
                    },
                    'unit_amount': int(course.price * 100),
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
                    course_id=payment.course_id
                )
                db.add(enrollment)
                await db.commit()
