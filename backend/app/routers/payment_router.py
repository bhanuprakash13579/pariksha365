"""Cashfree payment endpoints.

Two purchase surfaces:
  1. Notes bundle  — one-time, lifetime access to study PDFs.
  2. Exam stage    — time-boxed access to MOCK tests under a stage.

Flow for both:
  POST /cashfree/{notes|stage}/create-order  → get checkout_url
  ↓  user pays on Cashfree hosted page
  POST /cashfree/webhook                     → Cashfree notifies us (primary)
  GET  /cashfree/verify/{order_id}           → frontend verifies on return (belt-and-suspenders)

Notes download:
  GET  /notes/access                         → {has_access, files[]}
  GET  /notes/file/{book_id}                 → streams the PDF (auth + purchase gated)
"""
from __future__ import annotations

import asyncio
import io
import json
import os
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.exam_stage import ExamStage
from app.models.exam_stage_purchase import ExamStagePurchase
from app.models.notes import Note
from app.models.notes_purchase import NotesPurchase
from app.models.payment import (
    Payment, PaymentProvider, PaymentStatus,
    PAYMENT_TYPE_NOTES_BUNDLE, PAYMENT_TYPE_EXAM_STAGE,
)
from app.models.user import User
from app.schemas.payment_schema import CashfreeOrderResponse, NotesAccessResponse
from app.services import cashfree_service
from app.services.pdf_watermark_service import watermark_pdf
from app.services.r2_storage_service import r2_storage

router = APIRouter()

_BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
_NOTES_OUT = _BACKEND_DIR / "seeds" / "study_notes" / "_build" / "out"
_NOTES_MANIFEST = _BACKEND_DIR / "seeds" / "study_notes" / "_build" / "manifest.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _cf_order_id_notes(user_id: uuid.UUID) -> str:
    return f"notes-{user_id.hex[:8]}-{int(time.time())}"


def _cf_order_id_stage(stage_id: uuid.UUID, user_id: uuid.UUID) -> str:
    return f"stg-{stage_id.hex[:6]}-{user_id.hex[:6]}-{int(time.time())}"


def _notify_url() -> str:
    return f"{settings.BACKEND_URL.rstrip('/')}/api/v1/payments/cashfree/webhook"


def _local_notes_files() -> list[dict]:
    """Files baked into the deployment via manifest.json + local _build/out/."""
    if not _NOTES_MANIFEST.exists():
        return []
    try:
        doc = json.loads(_NOTES_MANIFEST.read_text())
    except Exception:
        return []
    files = []
    for book in doc.get("books", []):
        book_id = book.get("id", "")
        if not book_id:
            continue
        if (_NOTES_OUT / f"{book_id}.pdf").exists():
            files.append({
                "id": book_id,
                "title": book.get("title", ""),
                "filename": f"{book_id}.pdf",
                "download_url": f"/api/v1/payments/notes/file/{book_id}",
            })
    return files


async def _all_notes_files(db: AsyncSession) -> list[dict]:
    """Merge local manifest files with admin-uploaded DB files."""
    files = _local_notes_files()
    local_slugs = {f["id"] for f in files}

    db_notes = (await db.execute(
        select(Note).where(Note.is_visible == True, Note.slug.isnot(None))
    )).scalars().all()

    for note in db_notes:
        if note.slug not in local_slugs:
            files.append({
                "id": note.slug,
                "title": note.title or note.slug,
                "filename": f"{note.slug}.pdf",
                "download_url": f"/api/v1/payments/notes/file/{note.slug}",
            })
    return files


async def _fulfill_payment(db: AsyncSession, payment: Payment) -> None:
    """Grant entitlement after a confirmed payment. Idempotent."""
    payment.status = PaymentStatus.SUCCESS
    db.add(payment)

    if payment.payment_type == PAYMENT_TYPE_NOTES_BUNDLE:
        existing = (await db.execute(
            select(NotesPurchase).where(NotesPurchase.payment_id == payment.id)
        )).scalars().first()
        if not existing:
            db.add(NotesPurchase(
                user_id=payment.user_id,
                payment_id=payment.id,
                amount_paid_inr=int(payment.amount),
            ))

    elif payment.payment_type == PAYMENT_TYPE_EXAM_STAGE and payment.exam_stage_id:
        existing = (await db.execute(
            select(ExamStagePurchase).where(ExamStagePurchase.payment_id == payment.id)
        )).scalars().first()
        if not existing:
            stage = await db.get(ExamStage, payment.exam_stage_id)
            if stage:
                now = datetime.now(timezone.utc)
                db.add(ExamStagePurchase(
                    id=uuid.uuid4(),
                    user_id=payment.user_id,
                    exam_stage_id=payment.exam_stage_id,
                    amount_paid_inr=int(payment.amount),
                    validity_days_at_purchase=stage.validity_days,
                    purchased_at=now,
                    expires_at=now + timedelta(days=stage.validity_days),
                    payment_id=payment.id,
                    note="cashfree_payment",
                ))

    await db.commit()


# ---------------------------------------------------------------------------
# Create-order endpoints
# ---------------------------------------------------------------------------

@router.post("/cashfree/notes/create-order", response_model=CashfreeOrderResponse)
async def create_notes_order(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not settings.CASHFREE_APP_ID:
        raise HTTPException(status_code=503, detail="Payment gateway not configured")

    price = int(os.getenv("NOTES_PRICE_INR", "100"))
    cf_order_id = _cf_order_id_notes(current_user.id)
    frontend_url = settings.FRONTEND_URL.rstrip("/")

    payment = Payment(
        user_id=current_user.id,
        payment_type=PAYMENT_TYPE_NOTES_BUNDLE,
        amount=float(price),
        provider=PaymentProvider.CASHFREE,
        status=PaymentStatus.PENDING,
        transaction_id=cf_order_id,
    )
    db.add(payment)
    await db.commit()

    phone = (current_user.phone or "9999999999").strip() or "9999999999"
    order_data = await cashfree_service.create_order(
        order_id=cf_order_id,
        amount_inr=float(price),
        customer_id=str(current_user.id),
        customer_name=current_user.name,
        customer_email=current_user.email,
        customer_phone=phone,
        return_url=f"{frontend_url}/payment/return?order_id={cf_order_id}",
        notify_url=_notify_url(),
    )

    return CashfreeOrderResponse(
        checkout_url=cashfree_service.checkout_page_url(order_data["payment_session_id"]),
        cf_order_id=cf_order_id,
    )


@router.post("/cashfree/stage/{stage_id}/create-order", response_model=CashfreeOrderResponse)
async def create_stage_order(
    stage_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    if not settings.CASHFREE_APP_ID:
        raise HTTPException(status_code=503, detail="Payment gateway not configured")

    stage = await db.get(ExamStage, stage_id)
    if not stage:
        raise HTTPException(status_code=404, detail="Exam stage not found")
    if stage.price_inr <= 0:
        raise HTTPException(status_code=400, detail="This stage is free — no payment needed")

    cf_order_id = _cf_order_id_stage(stage_id, current_user.id)
    frontend_url = settings.FRONTEND_URL.rstrip("/")

    payment = Payment(
        user_id=current_user.id,
        exam_stage_id=stage_id,
        payment_type=PAYMENT_TYPE_EXAM_STAGE,
        amount=float(stage.price_inr),
        provider=PaymentProvider.CASHFREE,
        status=PaymentStatus.PENDING,
        transaction_id=cf_order_id,
    )
    db.add(payment)
    await db.commit()

    phone = (current_user.phone or "9999999999").strip() or "9999999999"
    order_data = await cashfree_service.create_order(
        order_id=cf_order_id,
        amount_inr=float(stage.price_inr),
        customer_id=str(current_user.id),
        customer_name=current_user.name,
        customer_email=current_user.email,
        customer_phone=phone,
        return_url=f"{frontend_url}/payment/return?order_id={cf_order_id}",
        notify_url=_notify_url(),
    )

    return CashfreeOrderResponse(
        checkout_url=cashfree_service.checkout_page_url(order_data["payment_session_id"]),
        cf_order_id=cf_order_id,
    )


# ---------------------------------------------------------------------------
# Webhook (primary fulfillment path — Cashfree calls this after payment)
# ---------------------------------------------------------------------------

@router.post("/cashfree/webhook")
async def cashfree_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> Any:
    raw_body = await request.body()
    timestamp = request.headers.get("x-webhook-timestamp", "")
    signature = request.headers.get("x-webhook-signature", "")

    if not cashfree_service.verify_webhook_signature(raw_body, timestamp, signature):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event = json.loads(raw_body)
    # Cashfree sends PAYMENT_SUCCESS_WEBHOOK on successful payment
    if event.get("type") not in ("PAYMENT_SUCCESS_WEBHOOK", "PAYMENT_SUCCESS"):
        return {"status": "ignored"}

    cf_order_id = (event.get("data") or {}).get("order", {}).get("order_id")
    if not cf_order_id:
        return {"status": "no_order_id"}

    result = await db.execute(
        select(Payment).where(Payment.transaction_id == cf_order_id)
    )
    payment = result.scalars().first()
    if not payment or payment.status == PaymentStatus.SUCCESS:
        return {"status": "already_processed_or_not_found"}

    await _fulfill_payment(db, payment)
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Verify on return redirect (belt-and-suspenders if webhook was slow)
# ---------------------------------------------------------------------------

@router.get("/cashfree/verify/{cf_order_id}")
async def verify_cashfree_order(
    cf_order_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    result = await db.execute(
        select(Payment).where(
            Payment.transaction_id == cf_order_id,
            Payment.user_id == current_user.id,
        )
    )
    payment = result.scalars().first()
    if not payment:
        raise HTTPException(status_code=404, detail="Order not found")

    if payment.status == PaymentStatus.SUCCESS:
        return _success_payload(payment)

    # Webhook hasn't fired yet — ask Cashfree directly
    order = await cashfree_service.get_order(cf_order_id)
    if order.get("order_status") == "PAID":
        await _fulfill_payment(db, payment)
        return _success_payload(payment)

    cf_status = order.get("order_status", "UNKNOWN")
    return {"status": "pending" if cf_status == "ACTIVE" else "failed", "cf_status": cf_status}


def _success_payload(payment: Payment) -> dict:
    return {
        "status": "success",
        "payment_type": payment.payment_type,
        "amount_paid": payment.amount,
        "exam_stage_id": str(payment.exam_stage_id) if payment.exam_stage_id else None,
    }


# ---------------------------------------------------------------------------
# Notes access + download
# ---------------------------------------------------------------------------

@router.get("/notes/access", response_model=NotesAccessResponse)
async def get_notes_access(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    purchase = (await db.execute(
        select(NotesPurchase).where(NotesPurchase.user_id == current_user.id)
    )).scalars().first()

    if not purchase:
        return NotesAccessResponse(has_access=False, files=[])
    return NotesAccessResponse(has_access=True, files=await _all_notes_files(db))


@router.get("/notes/file/{book_id}")
async def download_notes_file(
    book_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    purchase = (await db.execute(
        select(NotesPurchase).where(NotesPurchase.user_id == current_user.id)
    )).scalars().first()
    if not purchase:
        raise HTTPException(status_code=403, detail="Notes not purchased")

    safe_id = book_id.replace("/", "").replace("\\", "").replace("..", "").strip()

    # 1. Try local file (baked into deployment)
    local_path = _NOTES_OUT / f"{safe_id}.pdf"
    if local_path.exists():
        pdf_bytes = local_path.read_bytes()
    else:
        # 2. Try admin-uploaded file from R2 via DB
        note = (await db.execute(
            select(Note).where(Note.slug == safe_id, Note.is_visible == True)
        )).scalars().first()
        if not note:
            raise HTTPException(status_code=404, detail="File not found")
        loop = asyncio.get_event_loop()
        pdf_bytes = await loop.run_in_executor(None, r2_storage.download_notes_pdf, safe_id)
        if not pdf_bytes:
            raise HTTPException(status_code=404, detail="File not available in storage")

    # Watermark runs in a thread pool so it does not block the event loop
    loop = asyncio.get_event_loop()
    wm_bytes = await loop.run_in_executor(
        None,
        watermark_pdf,
        pdf_bytes,
        current_user.name,
        current_user.email,
        current_user.phone,
    )

    return StreamingResponse(
        io.BytesIO(wm_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="Pariksha365-{safe_id}.pdf"',
            "Content-Length": str(len(wm_bytes)),
        },
    )
