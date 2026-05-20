"""Exam-structure routes.

Split into two concerns:

* **Public** (``/api/v1/exam-structure``): anyone can read a pruned tree (only
  rows with ``is_enabled=True`` surface). This feeds the student Home screen.
* **Admin** (``/api/v1/admin/exam-structure``): returns the *full* tree including
  disabled rows, and exposes the visibility-toggle endpoints.

The admin routes here are deliberately separate from the legacy
``admin_router.py`` — exam-structure is a coherent surface and deserves its own
module for future growth (pattern CRUD, stage creation, etc.).
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas import exam_structure_schema as schema
from app.services import entitlement_service, exam_structure_service as service

public_router = APIRouter()
admin_router = APIRouter()


# --------------------------------------------------------------------------- #
# Public reads
# --------------------------------------------------------------------------- #

@public_router.get("", response_model=List[schema.CategoryWithStructureOut])
async def read_exam_structure(db: AsyncSession = Depends(get_db)):
    """Return the full Category ▸ SubCategory ▸ ExamStage ▸ Pattern tree
    with every node whose ``is_enabled`` is False pruned out.

    This is the single endpoint the student home screen calls to discover
    what's available.
    """
    return await service.list_structure_public(db)


# --------------------------------------------------------------------------- #
# Admin reads + toggles
# --------------------------------------------------------------------------- #

@admin_router.get("", response_model=List[schema.CategoryWithStructureOut])
async def admin_read_structure(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Unfiltered exam structure for the admin panel — includes disabled rows
    so the admin can toggle them back on.
    """
    return await service.list_structure_admin(db)


@admin_router.put(
    "/categories/{category_id}/visibility",
    response_model=schema.VisibilityToggleOut,
)
async def toggle_category_visibility(
    category_id: UUID,
    payload: schema.VisibilityToggleIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return await service.toggle_visibility(
        db, "category", category_id, payload.is_enabled
    )


@admin_router.put(
    "/subcategories/{subcategory_id}/visibility",
    response_model=schema.VisibilityToggleOut,
)
async def toggle_subcategory_visibility(
    subcategory_id: UUID,
    payload: schema.VisibilityToggleIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return await service.toggle_visibility(
        db, "subcategory", subcategory_id, payload.is_enabled
    )


@admin_router.put(
    "/exam-stages/{stage_id}/visibility",
    response_model=schema.VisibilityToggleOut,
)
async def toggle_exam_stage_visibility(
    stage_id: UUID,
    payload: schema.VisibilityToggleIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    return await service.toggle_visibility(
        db, "exam_stage", stage_id, payload.is_enabled
    )


# --------------------------------------------------------------------------- #
# Pricing (admin)
# --------------------------------------------------------------------------- #

@admin_router.put(
    "/exam-stages/{stage_id}/pattern",
    response_model=schema.ExamStageOut,
)
async def update_exam_stage_pattern(
    stage_id: UUID,
    payload: schema.ExamPatternCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Replace the ExamPattern (timing blueprint) attached to a stage.

    Use this when an exam board updates the notification — total duration,
    sectional timing flag, per-section question counts and per-section
    durations all flow through here. The student-facing player reads this
    pattern at attempt-time, so changes take effect on the very next attempt.

    Validation: section question_count and (when sectional timing is on)
    section duration_minutes MUST sum to the totals — see
    ``validate_pattern_sums``. Existing user attempts are not retroactively
    rescored — the timing change only affects future attempts.
    """
    return await service.replace_exam_pattern(db, stage_id=stage_id, pattern=payload)


@admin_router.put(
    "/exam-stages/{stage_id}/pricing",
    response_model=schema.ExamStageOut,
)
async def update_exam_stage_pricing(
    stage_id: UUID,
    payload: schema.ExamStagePricingUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Set price_inr and validity_days on a stage. Existing purchases keep
    their frozen validity window — this only affects future purchases.
    """
    return await entitlement_service.update_stage_pricing(db, stage_id, payload)


@admin_router.post(
    "/exam-stages/purchases/grant",
    response_model=schema.ExamStagePurchaseOut,
)
async def admin_grant_stage_purchase(
    payload: schema.AdminGrantPurchaseIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
):
    """Grant a stage entitlement without a payment. For support refunds,
    promo grants, beta testers. ``note`` is required for the audit trail.
    """
    return await entitlement_service.admin_grant(db, payload)


# --------------------------------------------------------------------------- #
# Access check + my-purchases (authenticated student)
# --------------------------------------------------------------------------- #

@public_router.get(
    "/exam-stages/{stage_id}/access",
    response_model=schema.ExamStageAccessOut,
)
async def get_stage_access(
    stage_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Tell the UI whether the user can currently access this stage's MOCKs,
    and if not, what it costs."""
    return await entitlement_service.resolve_stage_access(db, current_user.id, stage_id)


@public_router.get(
    "/purchases/me",
    response_model=List[schema.ExamStagePurchaseOut],
)
async def list_my_purchases(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Every entitlement this user has bought (or been granted). Powers the
    "My Access" list on the profile screen."""
    return await entitlement_service.list_user_purchases(db, current_user.id)
