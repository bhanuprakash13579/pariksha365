"""Load everything under ``backend/seeds/`` into the target database.

Covers four seed families, each idempotent:

1. **Exam structure** — ``seed_exam_structure.py``'s blueprint runs first
   so bodies/exams/stages/patterns exist before anything references them.
   Re-running is safe: service helpers fetch-or-create.
2. **PYQ test-series** — every ``seeds/pyq/<body>/<exam>/<stage>/<pdf-stem>.json``
   becomes a ``TestSeries`` with ``test_type='PYQ'``, its Section(s) and
   Question(s), linked to the matching ExamStage row. Key: we use the
   ``SeedTestSeries.id`` (deterministic ``pyq_paper_<sha>``) as the
   ``TestSeries.id``, so reloads upsert.
3. **Static-GK** — every ``seeds/static_gk/<subject-slug>/<topic_code>.json``
   streams into ``quiz_questions``. Dedup against existing rows by
   deterministic ID prefix ``sgk_<topic_code>_<seq>``.
4. **Answer patches** — already applied to the PYQ JSONs by
   ``apply_solutions``; nothing to do here since the JSONs already carry
   the merged state.

Run::

    python -m scripts.load_seeds                # loads everything
    python -m scripts.load_seeds --only pyq     # restrict to one family
    python -m scripts.load_seeds --dry-run      # plan without writing

Design notes
------------

* **Atomic per-file**. Each PYQ paper loads in its own transaction so a
  schema quirk in one file doesn't roll back the other 70. Failures are
  logged and counted; the loader continues.
* **Idempotent via deterministic IDs**. Re-running produces the same
  ``TestSeries.id`` / ``Section.id`` / ``Question.id`` / ``QuizQuestion.id``
  per source record, and we ``UPDATE`` in place rather than inserting
  duplicates.
* **Question.image_url** is populated from the first ``images[]`` entry
  in the seed JSON when present; extra images stay in the JSON for now
  and can move into a future ``question_images`` table without changing
  the loader.
* **Options**: seed JSON uses ``{option_text, is_correct}`` shape; that's
  exactly what the existing SQLAlchemy JSON column expects, so no
  reshaping needed — we just pass through.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import logging
import os
import sys
import uuid as _uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

# Import at module level so normalization is always in scope.
try:
    from scripts.topic_code_map import TOPIC_CODE_MAP as _TOPIC_CODE_MAP
except ImportError:
    _TOPIC_CODE_MAP = {}

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

log = logging.getLogger("load_seeds")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

_BACKEND = Path(__file__).resolve().parent.parent
_SEEDS = _BACKEND / "seeds"


# --------------------------------------------------------------------------- #
# Deterministic UUID mapper
# --------------------------------------------------------------------------- #
# We want every row created by the loader to have a stable UUID derived from
# the seed JSON's string ID so reloads UPDATE rather than INSERT duplicates.
# We use uuid5 with a per-domain namespace so different seed kinds can't
# accidentally collide on the same string.

_NS_TESTSERIES = _uuid.UUID("11111111-0000-0000-0000-000000000001")
_NS_SECTION = _uuid.UUID("11111111-0000-0000-0000-000000000002")
_NS_QUESTION = _uuid.UUID("11111111-0000-0000-0000-000000000003")
_NS_QUIZ_Q = _uuid.UUID("11111111-0000-0000-0000-000000000004")


def _uuid_for(namespace: _uuid.UUID, key: str) -> _uuid.UUID:
    return _uuid.uuid5(namespace, key)


# --------------------------------------------------------------------------- #
# Schema self-heal — runs once before any load step.
# --------------------------------------------------------------------------- #
# `Base.metadata.create_all` creates *new* tables but never adds columns to an
# already-existing table. Long-running prod databases drift behind the model
# whenever we add a column without a proper migration. Rather than ship a
# brittle Alembic chain we do a tiny, idempotent set of `ADD COLUMN IF NOT
# EXISTS` statements here so this loader is safe to run on any version of the
# prod schema. Postgres-only — sqlite skips because it always creates the
# columns from `Base.metadata.create_all`.
async def _self_heal_schema(db: AsyncSession) -> None:
    from sqlalchemy import text as _sql_text
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return
    statements = [
        # ExamStage pricing — added with the per-stage pricing model.
        "ALTER TABLE exam_stages ADD COLUMN IF NOT EXISTS price_inr INTEGER NOT NULL DEFAULT 0;",
        "ALTER TABLE exam_stages ADD COLUMN IF NOT EXISTS validity_days INTEGER NOT NULL DEFAULT 365;",
        # TestSeries real-exam timing snapshot (this release).
        "ALTER TABLE test_series ADD COLUMN IF NOT EXISTS total_duration_minutes INTEGER;",
        "ALTER TABLE test_series ADD COLUMN IF NOT EXISTS has_sectional_timing BOOLEAN NOT NULL DEFAULT FALSE;",
        "ALTER TABLE quiz_questions ADD COLUMN IF NOT EXISTS passage_id VARCHAR;",
    ]
    for stmt in statements:
        try:
            await db.execute(_sql_text(stmt))
        except Exception as e:
            # Don't abort the whole load on a single failed ALTER — just log.
            # Common failure: insufficient privilege for an unrelated column
            # the user has already removed. The loader will fail loudly
            # downstream if a *required* column is missing, which is the
            # right place to surface that.
            log.warning("self-heal skipped %r: %s", stmt, e)
    await db.commit()


# --------------------------------------------------------------------------- #
# Exam structure loading — reuse the seed_exam_structure module
# --------------------------------------------------------------------------- #

async def _load_exam_structure(db: AsyncSession, dry_run: bool = False) -> dict:
    from scripts.seed_exam_structure import EXAM_STRUCTURE
    from app.services import exam_structure_service as svc
    from app.schemas.exam_structure_schema import ExamPatternCreate

    counts = {"categories": 0, "subcategories": 0, "stages": 0, "patterns": 0}
    for body in EXAM_STRUCTURE:
        cat_meta = body["category"]
        cat = await svc.ensure_category(
            db, name=cat_meta["name"], order=cat_meta.get("order", 0),
            description=cat_meta.get("description"),
        )
        counts["categories"] += 1
        for sub_meta in body["subcategories"]:
            sub = await svc.ensure_subcategory(
                db, category=cat, name=sub_meta["name"], slug=sub_meta["slug"],
                order=sub_meta.get("order", 0), description=sub_meta.get("description"),
            )
            counts["subcategories"] += 1
            for stage_meta in sub_meta["stages"]:
                pattern = stage_meta.get("pattern")
                if pattern is not None:
                    svc.validate_pattern_sums(pattern)
                await svc.ensure_exam_stage_with_pattern(
                    db, subcategory=sub, name=stage_meta["name"],
                    slug=stage_meta["slug"], order=stage_meta.get("order", 0),
                    pattern=pattern,
                )
                counts["stages"] += 1
                if pattern is not None:
                    counts["patterns"] += 1
    if dry_run:
        await db.rollback()
    else:
        await db.commit()
    return counts


# --------------------------------------------------------------------------- #
# PYQ loader
# --------------------------------------------------------------------------- #

# Body-slug → production Category.name mapping. PYQ seed JSONs use lowercase
# plural slugs ("banks", "rrb") whereas prod categories use singular
# human-readable names ("Bank", "Railway"). Keeping this a static map is
# simpler than adding a ``category_slug`` column; there are only three
# real bodies, and the map is obvious at the call site.
_BODY_SLUG_TO_CATEGORY_NAME: Dict[str, str] = {
    "banks": "Bank",
    "ssc": "SSC",
    "rrb": "Railway",
    "upsc": "UPSC",
    # Keep identity mappings for any legacy slug that already matches a name
    "bank": "Bank",
    "railway": "Railway",
}


async def _resolve_exam_stage(
    db: AsyncSession, body_slug: str, exam_slug: str, stage_slug: str
) -> Optional[_uuid.UUID]:
    """Look up the ExamStage row for this (body, exam, stage).

    PYQ JSON ``body_slug`` values are lowercase / slug-style ("banks",
    "ssc", "rrb"); production ``Category.name`` uses human-readable
    singular form ("Bank", "SSC", "Railway"). The static map above bridges
    the two; any unmapped slug falls back to case-insensitive match
    against the raw slug so older content stays loadable.
    """
    from app.models.category import Category
    from app.models.subcategory import SubCategory
    from app.models.exam_stage import ExamStage

    category_name = _BODY_SLUG_TO_CATEGORY_NAME.get(body_slug.lower(), body_slug)

    stmt = (
        select(ExamStage.id)
        .join(SubCategory, SubCategory.id == ExamStage.subcategory_id)
        .join(Category, Category.id == SubCategory.category_id)
        .where(ExamStage.slug == stage_slug)
        .where(SubCategory.slug == exam_slug)
        .where(Category.name == category_name)
    )
    return (await db.execute(stmt)).scalar_one_or_none()


async def _load_one_pyq(db: AsyncSession, seed_path: Path, dry_run: bool = False, override_test_type: Optional[str] = None) -> dict:
    from app.models.test_series import TestSeries
    from app.models.section import Section
    from app.models.question import Question, DifficultyLevel
    from app.models.exam_pattern import ExamPattern, SectionPattern as _SP

    doc = json.loads(seed_path.read_text())
    ts_str_id = doc["id"]
    # Resolve test_type: explicit override (used by mock loader) wins, else
    # the seed JSON's own test_type field, else default to "PYQ" for legacy
    # seeds that don't set it explicitly.
    test_type_str = override_test_type or doc.get("test_type") or "PYQ"
    exam_stage_id = await _resolve_exam_stage(
        db, doc["body_slug"], doc["exam_slug"], doc["stage_slug"]
    )
    if exam_stage_id is None:
        return {"path": str(seed_path), "status": "skipped_no_exam_stage"}

    # Pull the canonical ExamPattern for this stage so we can stamp the test
    # series with real-exam timings instead of whatever the seed JSON happens
    # to carry. The pattern is the single source of truth — admin edits flow
    # straight into freshly-loaded papers.
    pattern_row = (await db.execute(
        select(ExamPattern).where(ExamPattern.exam_stage_id == exam_stage_id)
    )).scalar_one_or_none()
    section_patterns: list = []
    pattern_neg_mark: Optional[float] = None
    pattern_total_duration: Optional[int] = None
    pattern_has_sectional: bool = False
    if pattern_row is not None:
        section_patterns = list((await db.execute(
            select(_SP).where(_SP.exam_pattern_id == pattern_row.id).order_by(_SP.order)
        )).scalars().all())
        pattern_neg_mark = pattern_row.negative_mark_per_wrong
        pattern_total_duration = pattern_row.total_duration_minutes
        pattern_has_sectional = pattern_row.has_sectional_timing

    # Precedence: the PYQ paper's *own* timing wins over the current
    # ExamPattern. A 2023 IBPS PO paper that ran 60 min sectional should
    # stay 60 min sectional even if a later notification changes the format
    # — the candidate is rehearsing how that paper actually played out.
    #   1. PYQ JSON's explicit field
    #   2. Current ExamPattern as a fallback
    #   3. Hard-coded default
    neg_marking_doc = doc.get("negative_marking")
    neg_marking = (
        float(neg_marking_doc)
        if neg_marking_doc is not None
        else (pattern_neg_mark if pattern_neg_mark is not None else 0.0)
    )
    total_duration_doc = doc.get("total_duration_minutes")
    total_duration_override = doc.get("total_duration_override")
    if total_duration_override is not None:
        # Sectional fragments override the stage's full-paper duration so the
        # 30-Q DI practice doesn't show a 180-min timer.
        total_duration = int(total_duration_override)
    elif total_duration_doc is not None:
        total_duration = int(total_duration_doc)
    else:
        total_duration = pattern_total_duration
    # Sectional-timing flag: same precedence. Many PYQ JSONs don't carry
    # this flag explicitly, in which case we infer it from the per-section
    # time_limit_minutes (if every section has one) before falling back to
    # the current pattern.
    sectional_doc = doc.get("has_sectional_timing")
    inferred_sectional_from_doc: Optional[bool] = None
    sec_docs = doc.get("sections") or []
    if sec_docs:
        all_sections_timed = all(
            (s.get("time_limit_minutes") or 0) > 0 for s in sec_docs
        )
        if all_sections_timed:
            inferred_sectional_from_doc = True
    has_sectional_timing = (
        bool(sectional_doc)
        if sectional_doc is not None
        else (inferred_sectional_from_doc if inferred_sectional_from_doc is not None
              else pattern_has_sectional)
    )

    # If the seed paper has only a single combined section but the pattern
    # is multi-section, sectional timing MUST be off — you can't lock a
    # candidate inside one of one section. Force it false here, BEFORE the
    # TestSeries row is created, so the persisted row matches what the
    # section loop below will produce.
    seed_sections_for_check = doc.get("sections") or []
    if len(seed_sections_for_check) == 1 and (
        not section_patterns or len(section_patterns) > 1
    ):
        has_sectional_timing = False

    ts_uuid = _uuid_for(_NS_TESTSERIES, ts_str_id)
    # Upsert TestSeries. Use explicit select (not db.get) so we can mass-delete
    # dependent sections below via targeted DELETE rather than walking a lazy
    # collection — the latter triggers implicit I/O and fails in async mode.
    existing_ts = (await db.execute(
        select(TestSeries).where(TestSeries.id == ts_uuid)
    )).scalar_one_or_none()

    if existing_ts is None:
        ts = TestSeries(
            id=ts_uuid,
            title=doc["title"],
            description=doc.get("description"),
            negative_marking=neg_marking,
            # Initial publish state is False — the 100% completeness gate at
            # the end of this function will flip it to True only when the
            # paper has every Q clean AND matches the sanctioned count.
            is_published=False,
            test_type=test_type_str,
            exam_stage_id=exam_stage_id,
            source_pdf_path=doc.get("source_pdf_path"),
            paper_shift=doc.get("paper_shift"),
            total_duration_minutes=total_duration,
            has_sectional_timing=has_sectional_timing,
        )
        pd = doc.get("paper_date")
        if pd:
            try:
                ts.paper_date = datetime.fromisoformat(pd).date()
            except Exception:
                pass
        db.add(ts)
        await db.flush()
    else:
        # Keep admin-controlled fields (is_published) intact; refresh content
        existing_ts.title = doc["title"]
        existing_ts.description = doc.get("description")
        existing_ts.negative_marking = neg_marking
        existing_ts.exam_stage_id = exam_stage_id
        existing_ts.test_type = test_type_str
        existing_ts.source_pdf_path = doc.get("source_pdf_path")
        existing_ts.paper_shift = doc.get("paper_shift")
        existing_ts.total_duration_minutes = total_duration
        existing_ts.has_sectional_timing = has_sectional_timing
        # Bulk-delete existing questions then sections. The Section→Question
        # FK has no ON DELETE CASCADE at the DB level (ORM cascade only, which
        # doesn't apply to bulk SQL deletes), so we must delete children first.
        from sqlalchemy import delete as sa_delete
        await db.execute(
            sa_delete(Question).where(
                Question.section_id.in_(
                    select(Section.id).where(Section.test_series_id == ts_uuid)
                )
            )
        )
        await db.execute(sa_delete(Section).where(Section.test_series_id == ts_uuid))
        await db.flush()

    # Insert sections + questions, skipping unusable rows so prod never gets
    # blank stems / missing answer keys (would otherwise mark every attempt
    # wrong on those Qs and cripple PYQ scoring).
    q_count = 0
    skipped_breakdown = {"empty_stem": 0, "no_options": 0, "no_answer_key": 0}

    # When the seed structure mirrors the pattern (same number of sections),
    # we can reliably copy per-section timings. Most PYQ JSONs ship a single
    # "Full Paper" section, in which case positional matching against a
    # multi-section pattern would silently stamp the wrong duration onto the
    # only section. So we only do per-section matching when section counts
    # agree.
    seed_sections = doc.get("sections") or []
    sections_align = bool(section_patterns) and len(seed_sections) == len(section_patterns)

    def _match_section_pattern(sec_doc, sec_idx):
        if not sections_align:
            return None
        target = (sec_doc.get("name") or "").strip().lower()
        for sp in section_patterns:
            if (sp.name or "").strip().lower() == target:
                return sp
        # Same-count positional fallback (1-indexed) — safe because we only
        # take this branch when section counts already match.
        if 1 <= sec_idx <= len(section_patterns):
            return section_patterns[sec_idx - 1]
        return None

    # When the paper has a single combined section but the pattern is
    # multi-section, the single section's timer should equal the paper's
    # total duration, and the sectional-timing flag MUST be off (you can't
    # have sectional timing with one section). Recompute and propagate that
    # decision so the player gets a consistent signal.
    single_section_paper = len(seed_sections) == 1 and (
        not section_patterns or len(section_patterns) > 1
    )
    if single_section_paper and total_duration:
        has_sectional_timing = False

    for sec_idx, sec_doc in enumerate(seed_sections, start=1):
        sp_match = _match_section_pattern(sec_doc, sec_idx)
        if single_section_paper:
            # One section = full-paper timer.
            section_duration = sec_doc.get("time_limit_minutes") or total_duration
            section_marks = float(
                sec_doc.get("marks_per_question")
                or (section_patterns[0].marks_per_question if section_patterns else 1.0)
            )
        else:
            # Per-section duration: pattern wins when sectional timing is
            # enforced AND structures align. When sectional timing is off
            # we still record the pattern's duration_minutes if present so
            # analytics can compare per-section pace.
            section_duration = (
                sp_match.duration_minutes
                if sp_match is not None and sp_match.duration_minutes is not None
                else sec_doc.get("time_limit_minutes")
            )
            section_marks = (
                sp_match.marks_per_question
                if sp_match is not None and sp_match.marks_per_question is not None
                else float(sec_doc.get("marks_per_question") or 1.0)
            )
        sec_uuid = _uuid_for(_NS_SECTION, f"{ts_str_id}|{sec_idx}|{sec_doc['name']}")
        section = Section(
            id=sec_uuid,
            test_series_id=ts_uuid,
            name=sec_doc["name"],
            time_limit_minutes=section_duration,
            marks_per_question=section_marks,
            order_num=sec_doc.get("order", sec_idx),
        )
        db.add(section)
        await db.flush()
        # Re-number questions inside the section so skipped slots don't leave
        # gaps in order_num that would surface as "Q.7 then Q.9" to students.
        out_q_idx = 0
        for q_idx, q_doc in enumerate(sec_doc.get("questions", []), start=1):
            # ── Filter incomplete questions ───────────────────────────────
            raw_opts = q_doc.get("options") or []
            correct_idx = q_doc.get("correct_index")
            stem_raw = (q_doc.get("stem") or "").strip()
            # Empty / placeholder stem → unusable.
            if len(stem_raw) < 8:
                skipped_breakdown["empty_stem"] += 1
                continue
            # Need at least 2 options with non-empty text.
            opt_texts = [
                (o if isinstance(o, str) else (o.get("option_text") or o.get("text") or "")).strip()
                for o in raw_opts
            ]
            non_empty = [t for t in opt_texts if t]
            if len(non_empty) < 2:
                skipped_breakdown["no_options"] += 1
                continue
            # No answer key → can't score the question. Drop rather than
            # silently mark every option wrong.
            if correct_idx is None or not (0 <= correct_idx < len(opt_texts)):
                skipped_breakdown["no_answer_key"] += 1
                continue

            out_q_idx += 1
            # Compose the UUID key from (paper, section, q_index) — NOT from
            # q_doc["id"] alone. A handful of seed files have duplicate Q ids
            # (parser bug: two questions extracted with the same
            # printed_number in different page regions), and trusting the
            # seed id produces PK collisions on insert. This composite key
            # guarantees uniqueness within a paper.
            # Use the *source* q_idx (not out_q_idx) in the UUID key so reloads
            # remain idempotent even if the filter rules later change.
            q_uuid_key = f"{ts_str_id}|{sec_idx}|{q_idx}|{q_doc.get('id') or 'noid'}"
            q_uuid = _uuid_for(_NS_QUESTION, q_uuid_key)
            image_url = None
            if q_doc.get("images"):
                first = q_doc["images"][0]
                image_url = first.get("path") or first.get("url")
            diff_raw = (q_doc.get("difficulty") or "MEDIUM").upper()
            try:
                diff = DifficultyLevel[diff_raw]
            except KeyError:
                diff = DifficultyLevel.MEDIUM
            # Build options as {option_text, is_correct} to match the schema
            # the existing services expect.
            options_out: List[dict] = [
                {"option_text": t, "is_correct": (i == correct_idx)}
                for i, t in enumerate(opt_texts)
            ]
            # Prepend passage context to the stem if present — students need
            # to see the shared setup inline with the Q.
            stem = stem_raw
            if q_doc.get("passage_context"):
                stem = f"**Passage:** {q_doc['passage_context']}\n\n{stem}"
            question = Question(
                id=q_uuid,
                section_id=sec_uuid,
                question_text=stem,
                image_url=image_url,
                diagram_svg=q_doc.get("diagram_svg"),
                explanation=q_doc.get("explanation"),
                explanation_svg=q_doc.get("explanation_svg"),
                difficulty=diff,
                subject=q_doc.get("subject"),
                topic=q_doc.get("topic"),
                topic_code=q_doc.get("topic_code"),
                order_num=out_q_idx,
                options=options_out,
            )
            db.add(question)
            q_count += 1

    # ── 100% completeness gate ────────────────────────────────────────────
    # A paper publishes (visible to students) only when:
    #   1. zero questions were dropped, AND
    #   2. the clean Q count matches the sanctioned count from the linked
    #      ExamPattern (or, fallback, the seed JSON's own total_questions).
    #
    # Anything short of that is preserved in the DB but left UNPUBLISHED so
    # admin can re-publish manually after a fix. We refuse to ship half-broken
    # papers — a 79-Q paper labelled "IBPS PO Mains" misleads students who
    # expect 155 Qs.
    drop_total = sum(skipped_breakdown.values())
    # Sanctioned-count precedence:
    #   1. seed JSON's ``sanctioned_override`` — used by sectional-fragment
    #      papers (e.g. "SBI PO Mains DI Section Memory-Based" is a 30-Q
    #      sectional practice, not a 155-Q full Mains. Override lets it
    #      publish at 100% under its own honest count.)
    #   2. ExamPattern.total_questions — full-paper sanctioned count.
    #   3. seed JSON's ``total_questions`` — last-resort fallback.
    sanctioned_count = (
        doc.get("sanctioned_override")
        if doc.get("sanctioned_override") is not None
        else (pattern_row.total_questions if pattern_row is not None else doc.get("total_questions"))
    )
    # When the seed JSON pins a sanctioned_override, the override IS the
    # honest count for that paper — drops at extraction time were already
    # accounted for. Don't reject on drops in that case.
    has_override = doc.get("sanctioned_override") is not None
    is_complete = (
        sanctioned_count is not None
        and q_count == sanctioned_count
        and (drop_total == 0 or has_override)
    )
    gate_reason = None
    if not is_complete:
        if sanctioned_count is None:
            gate_reason = f"no sanctioned count to compare ({q_count} Qs loaded)"
        elif q_count != sanctioned_count:
            gate_reason = f"loaded {q_count}/{sanctioned_count} ({sanctioned_count - q_count} short)"
        if drop_total:
            d = (gate_reason + "; ") if gate_reason else ""
            gate_reason = f"{d}{drop_total} dropped {dict((k,v) for k,v in skipped_breakdown.items() if v)}"

    # Apply the gate. The TestSeries row was inserted with is_published=False
    # so we just flip it to True when fully complete; otherwise leave as-is.
    target_ts = ts if existing_ts is None else existing_ts
    target_ts.is_published = is_complete

    if dry_run:
        await db.rollback()
    else:
        await db.commit()
    return {
        "path": str(seed_path.relative_to(_SEEDS)),
        "status": "ok",
        "test_series_id": str(ts_uuid),
        "questions": q_count,
        "skipped": skipped_breakdown,
        "sanctioned": sanctioned_count,
        "is_published": is_complete,
        "gate_reason": gate_reason,
    }


async def _load_all_mocks(db: AsyncSession, limit: Optional[int], dry_run: bool = False) -> dict:
    """Walk seeds/mocks/ for compiled mock JSONs (skips *.blueprint.json /
    *.content.json — those are intermediate files for the generator pipeline)
    and loads each as test_type=MOCK using the same _load_one_pyq machinery."""
    mocks_root = _SEEDS / "mocks"
    if not mocks_root.exists():
        return {"papers_loaded": 0, "papers_published": 0, "papers_gated": 0,
                "papers_skipped": 0, "questions_loaded": 0, "failures": 0}
    files = [
        p for p in sorted(mocks_root.rglob("*.json"))
        if not p.name.startswith("_")
        and not p.name.endswith(".blueprint.json")
        and not p.name.endswith(".content.json")
    ]
    if limit:
        files = files[:limit]
    totals = {
        "papers_loaded": 0, "papers_published": 0, "papers_gated": 0,
        "papers_skipped": 0, "questions_loaded": 0, "failures": 0,
    }
    for f in files:
        try:
            result = await _load_one_pyq(db, f, dry_run=dry_run, override_test_type="MOCK")
            if result["status"] == "ok":
                totals["papers_loaded"] += 1
                totals["questions_loaded"] += result.get("questions", 0)
                if result.get("is_published"):
                    totals["papers_published"] += 1
                    log.info("PUBLISHED MOCK %s  (%d/%s Qs)",
                             result["path"], result["questions"], result.get("sanctioned"))
                else:
                    totals["papers_gated"] += 1
                    log.warning("GATED    MOCK %s  — %s",
                                result["path"], result.get("gate_reason"))
            else:
                totals["papers_skipped"] += 1
                log.warning("skipped MOCK %s — %s", result["path"], result["status"])
        except Exception:
            totals["failures"] += 1
            await db.rollback()
            log.exception("failed to load MOCK %s", f)
    return totals


async def _load_all_pyq(db: AsyncSession, limit: Optional[int], dry_run: bool = False) -> dict:
    pyq_root = _SEEDS / "pyq"
    files = [p for p in sorted(pyq_root.rglob("*.json")) if not p.name.startswith("_")]
    if limit:
        files = files[:limit]
    totals = {
        "papers_loaded": 0,
        "papers_published": 0,
        "papers_gated": 0,
        "papers_skipped": 0,
        "questions_loaded": 0,
        "questions_dropped_empty_stem": 0,
        "questions_dropped_no_options": 0,
        "questions_dropped_no_answer_key": 0,
        "failures": 0,
    }
    gated_papers: list[dict] = []
    for f in files:
        try:
            result = await _load_one_pyq(db, f, dry_run=dry_run)
            if result["status"] == "ok":
                totals["papers_loaded"] += 1
                totals["questions_loaded"] += result.get("questions", 0)
                sk = result.get("skipped") or {}
                totals["questions_dropped_empty_stem"] += sk.get("empty_stem", 0)
                totals["questions_dropped_no_options"] += sk.get("no_options", 0)
                totals["questions_dropped_no_answer_key"] += sk.get("no_answer_key", 0)
                drop_total = sum(sk.values()) if sk else 0
                if result.get("is_published"):
                    totals["papers_published"] += 1
                    log.info(
                        "PUBLISHED %s  (%d/%s Qs)",
                        result["path"], result["questions"], result.get("sanctioned"),
                    )
                else:
                    totals["papers_gated"] += 1
                    gated_papers.append({
                        "path": result["path"],
                        "loaded": result["questions"],
                        "sanctioned": result.get("sanctioned"),
                        "dropped": drop_total,
                        "reason": result.get("gate_reason"),
                    })
                    log.warning(
                        "GATED    %s  — %s",
                        result["path"], result.get("gate_reason"),
                    )
            else:
                totals["papers_skipped"] += 1
                log.warning("skipped %s — %s", result["path"], result["status"])
        except Exception:
            totals["failures"] += 1
            await db.rollback()
            log.exception("failed to load %s", f)
    if gated_papers:
        # Persist a machine-readable list so we know exactly what to recover.
        try:
            audit_dir = _SEEDS / "_audit"
            audit_dir.mkdir(exist_ok=True)
            (audit_dir / "gated_papers.json").write_text(
                json.dumps({"gated": gated_papers}, indent=2, ensure_ascii=False)
            )
            log.info("wrote gated-papers list to seeds/_audit/gated_papers.json")
        except Exception as e:
            log.warning("could not write gated_papers.json: %r", e)
    return totals


# --------------------------------------------------------------------------- #
# Static-GK loader
# --------------------------------------------------------------------------- #

async def _load_static_gk(db: AsyncSession, limit: Optional[int], dry_run: bool = False) -> dict:
    from app.models.quiz_pool import QuizQuestion

    gk_root = _SEEDS / "static_gk"
    if not gk_root.exists():
        return {"bundles_loaded": 0, "questions_loaded": 0, "questions_skipped_existing": 0}

    files = [p for p in sorted(gk_root.rglob("*.json")) if not p.name.startswith("_")]
    totals = {"bundles_loaded": 0, "questions_loaded": 0, "questions_skipped_existing": 0}
    count = 0
    for f in files:
        doc = json.loads(f.read_text())
        # Support both plain-list format (newer) and dict-wrapped {questions:[...]} format (older).
        q_docs = doc if isinstance(doc, list) else doc.get("questions", [])
        for q_doc in q_docs:
            count += 1
            if limit and count > limit:
                break
            qid = q_doc.get("id")
            q_uuid = _uuid_for(_NS_QUIZ_Q, qid) if qid else _uuid.uuid4()
            existing = await db.get(QuizQuestion, q_uuid)
            # Normalise options to {option_text, is_correct} regardless of source format.
            # Seeds may use {option_text, is_correct} or {letter, text, is_correct}.
            raw_opts = q_doc.get("options") or []
            options = [
                {
                    "option_text": (o.get("option_text") or o.get("text") or ""),
                    "is_correct": bool(o.get("is_correct", False)),
                }
                for o in raw_opts
            ]
            if existing is not None:
                totals["questions_skipped_existing"] += 1
                continue
            # CA-aware fields. Static-GK bundles leave these unset; CA
            # bundles (under seeds/static_gk/_current_affairs/) carry them
            # so the admin Current Affairs dashboard shows them as managed.
            from datetime import date as _date
            event_date = None
            valid_until = None
            try:
                if q_doc.get("event_date"):
                    event_date = _date.fromisoformat(q_doc["event_date"])
                if q_doc.get("valid_until"):
                    valid_until = _date.fromisoformat(q_doc["valid_until"])
            except Exception:
                pass

            _raw_tc = q_doc.get("topic_code") or ""
            db.add(QuizQuestion(
                id=q_uuid,
                question_text=(q_doc.get("stem") or q_doc.get("text") or ""),
                image_url=None,
                explanation=q_doc.get("explanation"),
                diagram_svg=q_doc.get("diagram_svg"),
                explanation_svg=q_doc.get("explanation_svg"),
                difficulty=(q_doc.get("difficulty") or "MEDIUM"),
                subject=q_doc.get("subject") or "General Knowledge",
                topic=q_doc.get("topic"),
                is_current_affair=bool(q_doc.get("is_current_affair", False)),
                event_date=event_date,
                valid_until=valid_until,
                is_published=bool(q_doc.get("is_published", True)),
                topic_code=_TOPIC_CODE_MAP.get(_raw_tc, _raw_tc) or None,
                passage_id=q_doc.get("passage_id"),
                options=options,
            ))
            totals["questions_loaded"] += 1
        if dry_run:
            await db.rollback()
        else:
            await db.commit()
        totals["bundles_loaded"] += 1
    return totals


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

async def run(only: Optional[str], limit: Optional[int], dry_run: bool) -> int:
    from app.core.database import async_session_maker

    results: Dict[str, dict] = {}
    async with async_session_maker() as db:
        # Schema self-heal first — before any SELECT / INSERT — so a prod DB
        # that's missing newly-added columns gets ADD COLUMN'd into shape and
        # the rest of the loader sees the schema it expects. No-op on sqlite.
        log.info("=== Schema self-heal ===")
        await _self_heal_schema(db)

        if only in (None, "structure"):
            log.info("=== Exam structure ===")
            results["exam_structure"] = await _load_exam_structure(db, dry_run=dry_run)
            log.info("structure: %s", results["exam_structure"])
        if only in (None, "pyq"):
            log.info("=== PYQ test-series ===")
            results["pyq"] = await _load_all_pyq(db, limit, dry_run=dry_run)
            log.info("pyq: %s", results["pyq"])
        if only in (None, "mocks", "mock"):
            log.info("=== Generated mock test-series ===")
            results["mocks"] = await _load_all_mocks(db, limit, dry_run=dry_run)
            log.info("mocks: %s", results["mocks"])
        if only in (None, "static_gk", "gk"):
            log.info("=== Static-GK quiz pool ===")
            results["static_gk"] = await _load_static_gk(db, limit, dry_run=dry_run)
            log.info("static_gk: %s", results["static_gk"])

    if dry_run:
        log.info("dry-run: all transactions rolled back; nothing was written")
    log.info("summary: %s", json.dumps(results, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=("structure", "pyq", "mocks", "static_gk"),
                    default=None, help="Restrict to one family (default: all)")
    ap.add_argument("--limit", type=int, default=None, help="Max items per family (for smoke tests)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--db-url", default=None,
                    help="Override DATABASE_URL (e.g. point at a staging DB)")
    ap.add_argument("--target", choices=("production",), default=None,
                    help="Shortcut: --target production pulls PRODUCTION_DB_URL from .env.local")
    args = ap.parse_args()

    if args.db_url:
        os.environ["DATABASE_URL"] = args.db_url
    elif args.target == "production":
        # Pull PRODUCTION_DB_URL from .env.local (gitignored) so you don't have
        # to export it every invocation. Never hard-coded here.
        env_local = _BACKEND / ".env.local"
        if env_local.exists():
            for line in env_local.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                if k.strip() == "PRODUCTION_DB_URL":
                    os.environ["DATABASE_URL"] = v.strip().strip('"').strip("'")
                    log.info("targeting production DB (credential redacted)")
                    break
        if not os.environ.get("DATABASE_URL"):
            log.error("--target=production set but PRODUCTION_DB_URL not in .env.local")
            return 2

    return asyncio.run(run(args.only, args.limit, args.dry_run))


if __name__ == "__main__":
    sys.exit(main())
