"""Per-ExamStage access control.

Two public surfaces:
  * ``has_active_stage_access`` / ``resolve_stage_access`` — read-only checks
    used by the attempt-start gate and the student "Buy Access" UI.
  * ``record_purchase`` / ``admin_grant`` — write paths; grant creates an
    entitlement row without touching the payments table (used for support
    refunds and promo grants), record_purchase is called by the Razorpay
    webhook once that's wired.

Access rule (single source of truth — don't duplicate this logic in callers):

  1. PYQ ``test_series`` → always free. The stage's price is irrelevant.
  2. MOCK ``test_series`` under a stage with price_inr == 0 → free.
  3. MOCK ``test_series`` under a priced stage →
     requires a row in ``exam_stage_purchases`` for (user, stage) with
     ``expires_at > NOW()``.

The first two cases are admin policy (PYQ-free-forever is a product commitment;
see memory:project_overview). Only case 3 actually consults the purchases
table, so this service stays cheap even when most content is free.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.exam_stage import ExamStage
from app.models.exam_stage_purchase import ExamStagePurchase
from app.models.test_series import TestSeries, TestType
from app.schemas import exam_structure_schema as schema


# --------------------------------------------------------------------------- #
# Read path
# --------------------------------------------------------------------------- #

async def _latest_active_purchase(
    db: AsyncSession, user_id: UUID, stage_id: UUID
) -> Optional[ExamStagePurchase]:
    now = datetime.now(timezone.utc)
    stmt = (
        select(ExamStagePurchase)
        .where(
            ExamStagePurchase.user_id == user_id,
            ExamStagePurchase.exam_stage_id == stage_id,
            ExamStagePurchase.expires_at > now,
        )
        .order_by(ExamStagePurchase.expires_at.desc())
    )
    return (await db.execute(stmt)).scalars().first()


async def has_active_stage_access(
    db: AsyncSession, user_id: UUID, stage_id: UUID
) -> bool:
    """True if the user can currently access MOCK content under this stage.

    Pure boolean — for UI / audit use ``resolve_stage_access`` which carries
    the price and expiry too.
    """
    stage = await db.get(ExamStage, stage_id)
    if stage is None:
        return False
    if stage.price_inr == 0:
        return True
    return (await _latest_active_purchase(db, user_id, stage_id)) is not None


async def resolve_stage_access(
    db: AsyncSession, user_id: UUID, stage_id: UUID
) -> schema.ExamStageAccessOut:
    """Detailed access info for the student UI — powers the "Buy Access /
    Access active until X" strip on the stage card.
    """
    stage = await db.get(ExamStage, stage_id)
    if stage is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

    if stage.price_inr == 0:
        return schema.ExamStageAccessOut(
            exam_stage_id=stage.id,
            is_free=True,
            has_active_access=True,
            price_inr=0,
            validity_days=stage.validity_days,
            expires_at=None,
        )

    active = await _latest_active_purchase(db, user_id, stage_id)
    return schema.ExamStageAccessOut(
        exam_stage_id=stage.id,
        is_free=False,
        has_active_access=active is not None,
        price_inr=stage.price_inr,
        validity_days=stage.validity_days,
        expires_at=active.expires_at if active else None,
    )


async def ensure_test_series_access(
    db: AsyncSession, user_id: UUID, test_series: TestSeries
) -> None:
    """Gate used by attempt-start. Raises 402 with a structured payload the
    frontend uses to route the user to the checkout screen.

    Does NOT replace the legacy folder/enrollment gate — it's a *new* gate that
    runs before that one. Rule:
      * PYQ → no gate, return immediately.
      * MOCK with no exam_stage → fall through (legacy course gate handles it).
      * MOCK with a free stage → no gate.
      * MOCK with a priced stage → require entitlement.
    """
    if test_series.test_type == TestType.PYQ:
        return
    if test_series.exam_stage_id is None:
        return  # legacy path; caller still runs folder/enrollment checks

    stage = await db.get(ExamStage, test_series.exam_stage_id)
    if stage is None or stage.price_inr == 0:
        return

    active = await _latest_active_purchase(db, user_id, stage.id)
    if active is not None:
        return

    # HTTP 402 Payment Required — carries structured details so the FE can
    # render a "Buy Access" CTA without extra lookups.
    raise HTTPException(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        detail={
            "reason": "stage_access_required",
            "exam_stage_id": str(stage.id),
            "price_inr": stage.price_inr,
            "validity_days": stage.validity_days,
        },
    )


# --------------------------------------------------------------------------- #
# Write path
# --------------------------------------------------------------------------- #

async def record_purchase(
    db: AsyncSession,
    *,
    user_id: UUID,
    stage_id: UUID,
    amount_paid_inr: int,
    validity_days: int,
    payment_id: Optional[UUID] = None,
    note: Optional[str] = None,
) -> ExamStagePurchase:
    """Create an entitlement row. Caller is responsible for having confirmed
    the payment before calling (webhook verification, admin intent, etc.).

    ``validity_days`` is frozen at purchase time — later admin edits to the
    stage's validity_days will NOT shorten the already-purchased window.
    """
    now = datetime.now(timezone.utc)
    row = ExamStagePurchase(
        id=uuid4(),
        user_id=user_id,
        exam_stage_id=stage_id,
        amount_paid_inr=amount_paid_inr,
        validity_days_at_purchase=validity_days,
        purchased_at=now,
        expires_at=now + timedelta(days=validity_days),
        payment_id=payment_id,
        note=note,
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return row


async def admin_grant(
    db: AsyncSession, payload: schema.AdminGrantPurchaseIn
) -> ExamStagePurchase:
    """Admin-only: grant access without a payment. amount_paid_inr=0, note
    stored for audit. Use for support refunds, promo codes, beta testers.
    """
    stage = await db.get(ExamStage, payload.exam_stage_id)
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    return await record_purchase(
        db,
        user_id=payload.user_id,
        stage_id=payload.exam_stage_id,
        amount_paid_inr=0,
        validity_days=payload.validity_days,
        note=f"[admin-grant] {payload.note}",
    )


# --------------------------------------------------------------------------- #
# Pricing admin
# --------------------------------------------------------------------------- #

async def update_stage_pricing(
    db: AsyncSession, stage_id: UUID, payload: schema.ExamStagePricingUpdate
) -> ExamStage:
    """Set price and validity on a stage. Existing entitlements are
    untouched — their ``validity_days_at_purchase`` was frozen at purchase
    time, so changing the stage's validity only affects *future* purchases.
    """
    stage = await db.get(ExamStage, stage_id)
    if stage is None:
        raise HTTPException(status_code=404, detail="Stage not found")
    stage.price_inr = payload.price_inr
    stage.validity_days = payload.validity_days
    await db.commit()
    await db.refresh(stage)
    return stage


async def list_user_purchases(
    db: AsyncSession, user_id: UUID
) -> list[ExamStagePurchase]:
    """All entitlements for a user, newest first. Drives the "My Access"
    screen in the student profile.
    """
    stmt = (
        select(ExamStagePurchase)
        .where(ExamStagePurchase.user_id == user_id)
        .order_by(ExamStagePurchase.purchased_at.desc())
    )
    return list((await db.execute(stmt)).scalars().all())
