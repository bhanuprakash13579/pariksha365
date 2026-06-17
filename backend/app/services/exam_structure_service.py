"""Service layer for the exam-structure backbone.

Contains:
  * ``list_structure_admin`` / ``list_structure_public``  — hierarchical reads
  * ``toggle_visibility``  — flip ``is_enabled`` on a Category, SubCategory, or
                             ExamStage
  * ``upsert_exam_stage``   — create or replace an ExamStage with its pattern
                              (used by the seed script and by future admin UI)
  * helpers for fetching a stage by its (body slug, exam slug, stage slug)
    triple, used by the student-facing routes

All reads use ``selectinload`` so the nested structure (Category ▸ SubCategory ▸
ExamStage ▸ ExamPattern ▸ SectionPattern) comes back in one round-trip. Writes
commit atomically; on validation failure the DB transaction is rolled back.
"""
from __future__ import annotations

from typing import Iterable, Literal, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.category import Category
from app.models.exam_pattern import ExamPattern, SectionPattern
from app.models.exam_stage import ExamStage
from app.models.subcategory import SubCategory
from app.models.test_series import TestSeries
from app.schemas import exam_structure_schema as schema

EntityType = Literal["category", "subcategory", "exam_stage"]


# --------------------------------------------------------------------------- #
# Read helpers
# --------------------------------------------------------------------------- #

def _structure_load_options():
    """Eager-loading plan shared by public and admin reads."""
    return [
        selectinload(Category.subcategories)
        .selectinload(SubCategory.exam_stages)
        .selectinload(ExamStage.exam_pattern)
        .selectinload(ExamPattern.section_patterns),
        selectinload(Category.subcategories)
        .selectinload(SubCategory.exam_stages)
        .selectinload(ExamStage.test_series),
    ]


async def list_structure_admin(db: AsyncSession) -> list[Category]:
    """Return the full Category ▸ SubCategory ▸ ExamStage ▸ Pattern tree
    unfiltered — for the admin panel, which needs to see disabled rows to
    toggle them.
    """
    stmt = (
        select(Category)
        .options(*_structure_load_options())
        .order_by(Category.order, Category.name)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def list_structure_public(db: AsyncSession) -> list[Category]:
    """Return the structure with every disabled node pruned.

    The filter is applied in Python after the eager load; the alternative —
    filtering at each join — produces hard-to-read SQL and still needs
    post-processing because we want a disabled stage to hide, not to surface
    as an empty stub. The post-load filter is O(N) in nodes and trivial.
    """
    categories = await list_structure_admin(db)
    visible: list[Category] = []
    for cat in categories:
        if not cat.is_enabled:
            continue
        cat.subcategories = [
            _prune_stages(sub)
            for sub in cat.subcategories
            if sub.is_enabled
        ]
        if cat.subcategories:
            visible.append(cat)
    return visible


def _prune_stages(sub: SubCategory) -> SubCategory:
    for stage in sub.exam_stages:
        stage.test_series = [ts for ts in stage.test_series if ts.is_published]
    sub.exam_stages = [st for st in sub.exam_stages if st.is_enabled]
    return sub


async def get_stage_by_slug(
    db: AsyncSession, body_slug: str, exam_slug: str, stage_slug: str
) -> Optional[ExamStage]:
    """Resolve a stage using the (category, subcategory, stage) slug triple —
    the canonical URL shape the frontend uses.
    """
    stmt = (
        select(ExamStage)
        .join(SubCategory, SubCategory.id == ExamStage.subcategory_id)
        .join(Category, Category.id == SubCategory.category_id)
        .options(
            selectinload(ExamStage.exam_pattern).selectinload(ExamPattern.section_patterns)
        )
        .where(ExamStage.slug == stage_slug)
        .where(SubCategory.slug == exam_slug)
        .where(Category.name.ilike(body_slug.replace("-", " ")))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


# --------------------------------------------------------------------------- #
# Published tests (student-facing)
# --------------------------------------------------------------------------- #

async def list_published_tests(
    db: AsyncSession,
    *,
    category_id: Optional[UUID] = None,
    subcategory_id: Optional[UUID] = None,
    test_type: Optional[str] = None,
) -> list[dict]:
    """Return all published TestSeries rows linked to an exam stage, with the
    stage / subcategory / category context denormalised onto each row.

    Filters (all optional):
      * ``category_id``    — restrict to one category
      * ``subcategory_id`` — restrict to one subcategory (used by mobile)
      * ``test_type``      — "MOCK" or "PYQ"

    Source of truth is ``TestSeries.is_published`` — the admin flipped that
    flag in the publish-toggle UI, so the test should appear to students.
    We do NOT additionally require ExamStage / SubCategory / Category
    ``is_enabled`` cascade: those flags exist for staging entire branches
    of the catalogue and the visibility self-heal in main.py only flips
    Category + SubCategory, never ExamStage — so requiring stage.is_enabled
    here permanently hid published tests for any stage the admin never
    manually toggled on. If an admin wants to hide an entire stage they
    can unpublish its tests; the publish flag is the authoritative signal.
    """
    stmt = (
        select(
            TestSeries,
            ExamStage.id.label("stage_id"),
            ExamStage.name.label("stage_name"),
            SubCategory.id.label("subcategory_id"),
            SubCategory.name.label("subcategory_name"),
            Category.id.label("category_id"),
            Category.name.label("category_name"),
        )
        .join(ExamStage, ExamStage.id == TestSeries.exam_stage_id)
        .join(SubCategory, SubCategory.id == ExamStage.subcategory_id)
        .join(Category, Category.id == SubCategory.category_id)
        .where(TestSeries.is_published.is_(True))
        .where(TestSeries.exam_stage_id.isnot(None))
    )
    if category_id is not None:
        stmt = stmt.where(Category.id == category_id)
    if subcategory_id is not None:
        stmt = stmt.where(SubCategory.id == subcategory_id)
    if test_type is not None:
        stmt = stmt.where(TestSeries.test_type == test_type)

    stmt = stmt.order_by(TestSeries.test_type, TestSeries.paper_date.desc().nullslast(), TestSeries.title)

    rows = (await db.execute(stmt)).all()

    out = []
    for row in rows:
        ts: TestSeries = row[0]
        out.append(
            schema.PublishedTestOut(
                id=ts.id,
                title=ts.title,
                test_type=ts.test_type.value if hasattr(ts.test_type, "value") else str(ts.test_type),
                total_questions=None,  # avoid lazy-load; client infers from pattern if needed
                total_duration_minutes=ts.total_duration_minutes,
                has_sectional_timing=ts.has_sectional_timing,
                negative_marking=ts.negative_marking,
                paper_date=str(ts.paper_date) if ts.paper_date else None,
                paper_shift=ts.paper_shift,
                stage_id=row.stage_id,
                stage_name=row.stage_name,
                subcategory_id=row.subcategory_id,
                subcategory_name=row.subcategory_name,
                category_id=row.category_id,
                category_name=row.category_name,
            )
        )
    return out


# --------------------------------------------------------------------------- #
# Visibility toggle
# --------------------------------------------------------------------------- #

_ENTITY_MODEL = {
    "category": Category,
    "subcategory": SubCategory,
    "exam_stage": ExamStage,
}


async def toggle_visibility(
    db: AsyncSession, entity: EntityType, entity_id: UUID, is_enabled: bool
) -> schema.VisibilityToggleOut:
    """Flip ``is_enabled`` on one Category / SubCategory / ExamStage.

    Raises 404 if the target row is missing. Does **not** cascade — disabling a
    Category doesn't auto-disable its SubCategories; the public read path
    already prunes any descendant whose ancestor is disabled, so a cascade
    would only make re-enabling annoying.
    """
    Model = _ENTITY_MODEL.get(entity)
    if Model is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown entity type: {entity!r}",
        )
    row = await db.get(Model, entity_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} {entity_id} not found",
        )
    row.is_enabled = is_enabled
    await db.commit()
    return schema.VisibilityToggleOut(
        id=entity_id, is_enabled=is_enabled, entity=entity
    )


# --------------------------------------------------------------------------- #
# Seed / upsert helpers
# --------------------------------------------------------------------------- #

async def ensure_category(
    db: AsyncSession, *, name: str, order: int = 0, description: Optional[str] = None
) -> Category:
    """Fetch-or-create a Category by name. ``is_enabled`` is left untouched on
    existing rows so re-running the seed script never disables something the
    admin has already turned on.
    """
    stmt = select(Category).where(Category.name == name)
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    cat = Category(name=name, order=order, description=description, is_enabled=False)
    db.add(cat)
    await db.flush()
    return cat


async def ensure_subcategory(
    db: AsyncSession,
    *,
    category: Category,
    name: str,
    slug: str,
    order: int = 0,
    description: Optional[str] = None,
) -> SubCategory:
    stmt = select(SubCategory).where(
        SubCategory.category_id == category.id, SubCategory.slug == slug
    )
    existing = (await db.execute(stmt)).scalar_one_or_none()
    if existing is not None:
        return existing
    sub = SubCategory(
        category_id=category.id,
        name=name,
        slug=slug,
        order=order,
        description=description,
        is_enabled=False,
    )
    db.add(sub)
    await db.flush()
    return sub


async def ensure_exam_stage_with_pattern(
    db: AsyncSession,
    *,
    subcategory: SubCategory,
    name: str,
    slug: str,
    order: int,
    pattern: Optional[schema.ExamPatternCreate],
) -> ExamStage:
    """Fetch-or-create an ExamStage, replacing its ExamPattern (and child
    SectionPattern rows) with the supplied blueprint if given.

    Replace-in-place is deliberate: the pattern is considered authoritative
    config; re-seeding with an updated pattern should win, while ``is_enabled``
    on the stage itself is preserved so admin intent isn't clobbered.
    """
    stmt = (
        select(ExamStage)
        .options(
            selectinload(ExamStage.exam_pattern).selectinload(ExamPattern.section_patterns)
        )
        .where(ExamStage.subcategory_id == subcategory.id, ExamStage.slug == slug)
    )
    stage = (await db.execute(stmt)).scalar_one_or_none()
    stage_was_new = stage is None

    if stage is None:
        stage = ExamStage(
            subcategory_id=subcategory.id,
            name=name,
            slug=slug,
            order=order,
            is_enabled=False,
        )
        db.add(stage)
        await db.flush()
    else:
        # keep is_enabled; refresh display name/order
        stage.name = name
        stage.order = order

    if pattern is not None:
        # replace-in-place: drop the old pattern (cascades to section_patterns).
        # When the stage was just created we KNOW there's no existing pattern —
        # skip the relationship access to avoid lazy-loading in async context.
        if not stage_was_new and stage.exam_pattern is not None:
            await db.delete(stage.exam_pattern)
            await db.flush()
        ep = ExamPattern(
            exam_stage_id=stage.id,
            total_duration_minutes=pattern.total_duration_minutes,
            total_questions=pattern.total_questions,
            total_marks=pattern.total_marks,
            negative_mark_per_wrong=pattern.negative_mark_per_wrong,
            has_sectional_timing=pattern.has_sectional_timing,
            notes=pattern.notes,
        )
        db.add(ep)
        await db.flush()
        for sp in pattern.section_patterns:
            db.add(
                SectionPattern(
                    exam_pattern_id=ep.id,
                    name=sp.name,
                    subject=sp.subject,
                    question_count=sp.question_count,
                    duration_minutes=sp.duration_minutes,
                    marks_per_question=sp.marks_per_question,
                    order=sp.order,
                )
            )
        await db.flush()
    return stage


async def replace_exam_pattern(
    db: AsyncSession, *, stage_id: UUID, pattern: schema.ExamPatternCreate
) -> ExamStage:
    """Admin-facing replace-in-place for a stage's ExamPattern.

    Validates the section sums first (raises 400 on inconsistency), then
    drops any existing pattern for the stage and writes the new one with its
    section_patterns. The stage's ``is_enabled`` and pricing are untouched —
    timing is the only thing changing here. Returns the refreshed ExamStage
    with its pattern eager-loaded so the response payload is complete.
    """
    validate_pattern_sums(pattern)

    stmt = (
        select(ExamStage)
        .options(
            selectinload(ExamStage.exam_pattern).selectinload(ExamPattern.section_patterns)
        )
        .where(ExamStage.id == stage_id)
    )
    stage = (await db.execute(stmt)).scalar_one_or_none()
    if stage is None:
        raise HTTPException(status_code=404, detail="Exam stage not found")

    if stage.exam_pattern is not None:
        await db.delete(stage.exam_pattern)
        await db.flush()

    ep = ExamPattern(
        exam_stage_id=stage.id,
        total_duration_minutes=pattern.total_duration_minutes,
        total_questions=pattern.total_questions,
        total_marks=pattern.total_marks,
        negative_mark_per_wrong=pattern.negative_mark_per_wrong,
        has_sectional_timing=pattern.has_sectional_timing,
        notes=pattern.notes,
    )
    db.add(ep)
    await db.flush()
    for sp in pattern.section_patterns:
        db.add(
            SectionPattern(
                exam_pattern_id=ep.id,
                name=sp.name,
                subject=sp.subject,
                question_count=sp.question_count,
                duration_minutes=sp.duration_minutes,
                marks_per_question=sp.marks_per_question,
                order=sp.order,
            )
        )
    await db.commit()

    # Re-load with eager pattern + sections for the response.
    refreshed = (await db.execute(stmt)).scalar_one()
    return refreshed


def validate_pattern_sums(pattern: schema.ExamPatternCreate) -> None:
    """Guard against internally inconsistent patterns: ensure section Qs sum to
    ``total_questions``, and — when sectional timing is on — section durations
    sum to ``total_duration_minutes``.

    Raises HTTPException(400) with a descriptive message. Called from the
    seed script and should also be wired into any future admin-create endpoint.
    """
    total_sq = sum(sp.question_count for sp in pattern.section_patterns)
    if total_sq != pattern.total_questions:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Section question counts sum to {total_sq} but total_questions "
                f"is {pattern.total_questions}"
            ),
        )
    if pattern.has_sectional_timing:
        missing = [sp.name for sp in pattern.section_patterns if sp.duration_minutes is None]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=(
                    "has_sectional_timing is true but these sections lack "
                    f"duration_minutes: {missing}"
                ),
            )
        total_sd = sum(sp.duration_minutes or 0 for sp in pattern.section_patterns)
        if total_sd != pattern.total_duration_minutes:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Section durations sum to {total_sd} min but "
                    f"total_duration_minutes is {pattern.total_duration_minutes}"
                ),
            )
