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


async def _load_one_pyq(db: AsyncSession, seed_path: Path, dry_run: bool = False) -> dict:
    from app.models.test_series import TestSeries
    from app.models.section import Section
    from app.models.question import Question, DifficultyLevel

    doc = json.loads(seed_path.read_text())
    ts_str_id = doc["id"]
    exam_stage_id = await _resolve_exam_stage(
        db, doc["body_slug"], doc["exam_slug"], doc["stage_slug"]
    )
    if exam_stage_id is None:
        return {"path": str(seed_path), "status": "skipped_no_exam_stage"}

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
            negative_marking=float(doc.get("negative_marking") or 0.0),
            is_published=True,
            test_type="PYQ",
            exam_stage_id=exam_stage_id,
            source_pdf_path=doc.get("source_pdf_path"),
            paper_shift=doc.get("paper_shift"),
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
        existing_ts.negative_marking = float(doc.get("negative_marking") or 0.0)
        existing_ts.exam_stage_id = exam_stage_id
        existing_ts.test_type = "PYQ"
        existing_ts.source_pdf_path = doc.get("source_pdf_path")
        existing_ts.paper_shift = doc.get("paper_shift")
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

    # Insert sections + questions
    q_count = 0
    for sec_idx, sec_doc in enumerate(doc.get("sections", []), start=1):
        sec_uuid = _uuid_for(_NS_SECTION, f"{ts_str_id}|{sec_idx}|{sec_doc['name']}")
        section = Section(
            id=sec_uuid,
            test_series_id=ts_uuid,
            name=sec_doc["name"],
            time_limit_minutes=sec_doc.get("time_limit_minutes"),
            marks_per_question=float(sec_doc.get("marks_per_question") or 1.0),
            order_num=sec_doc.get("order", sec_idx),
        )
        db.add(section)
        await db.flush()
        for q_idx, q_doc in enumerate(sec_doc.get("questions", []), start=1):
            # Compose the UUID key from (paper, section, q_index) — NOT from
            # q_doc["id"] alone. A handful of seed files have duplicate Q ids
            # (parser bug: two questions extracted with the same
            # printed_number in different page regions), and trusting the
            # seed id produces PK collisions on insert. This composite key
            # guarantees uniqueness within a paper.
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
            raw_opts = q_doc.get("options") or []
            correct_idx = q_doc.get("correct_index")
            options_out: List[dict] = []
            for i, opt in enumerate(raw_opts):
                text = opt if isinstance(opt, str) else (opt.get("option_text") or opt.get("text") or "")
                options_out.append({
                    "option_text": text,
                    "is_correct": (i == correct_idx) if correct_idx is not None else False,
                })
            # Prepend passage context to the stem if present — students need
            # to see the shared setup inline with the Q.
            stem = q_doc["stem"]
            if q_doc.get("passage_context"):
                stem = f"**Passage:** {q_doc['passage_context']}\n\n{stem}"
            question = Question(
                id=q_uuid,
                section_id=sec_uuid,
                question_text=stem,
                image_url=image_url,
                explanation=q_doc.get("explanation"),
                difficulty=diff,
                subject=q_doc.get("subject"),
                topic=q_doc.get("topic"),
                topic_code=q_doc.get("topic_code"),
                order_num=q_idx,
                options=options_out,
            )
            db.add(question)
            q_count += 1
    if dry_run:
        await db.rollback()
    else:
        await db.commit()
    return {"path": str(seed_path.relative_to(_SEEDS)), "status": "ok",
            "test_series_id": str(ts_uuid), "questions": q_count}


async def _load_all_pyq(db: AsyncSession, limit: Optional[int], dry_run: bool = False) -> dict:
    pyq_root = _SEEDS / "pyq"
    files = [p for p in sorted(pyq_root.rglob("*.json")) if not p.name.startswith("_")]
    if limit:
        files = files[:limit]
    totals = {"papers_loaded": 0, "papers_skipped": 0, "questions_loaded": 0, "failures": 0}
    for f in files:
        try:
            result = await _load_one_pyq(db, f, dry_run=dry_run)
            if result["status"] == "ok":
                totals["papers_loaded"] += 1
                totals["questions_loaded"] += result.get("questions", 0)
                log.info("loaded %s  (%d Qs)", result["path"], result["questions"])
            else:
                totals["papers_skipped"] += 1
                log.warning("skipped %s — %s", result["path"], result["status"])
        except Exception:
            totals["failures"] += 1
            await db.rollback()
            log.exception("failed to load %s", f)
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
        for q_doc in doc.get("questions", []):
            count += 1
            if limit and count > limit:
                break
            qid = q_doc.get("id")
            q_uuid = _uuid_for(_NS_QUIZ_Q, qid) if qid else _uuid.uuid4()
            existing = await db.get(QuizQuestion, q_uuid)
            # The production table uses the same JSON options shape —
            # {option_text, is_correct} — so we pass through as-is.
            options = q_doc.get("options") or []
            if existing is not None:
                totals["questions_skipped_existing"] += 1
                continue
            db.add(QuizQuestion(
                id=q_uuid,
                question_text=q_doc["stem"],
                image_url=None,
                explanation=q_doc.get("explanation"),
                difficulty=(q_doc.get("difficulty") or "MEDIUM"),
                subject=q_doc.get("subject") or "General Knowledge",
                topic=q_doc.get("topic"),
                topic_code=q_doc.get("topic_code"),
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
        if only in (None, "structure"):
            log.info("=== Exam structure ===")
            results["exam_structure"] = await _load_exam_structure(db, dry_run=dry_run)
            log.info("structure: %s", results["exam_structure"])
        if only in (None, "pyq"):
            log.info("=== PYQ test-series ===")
            results["pyq"] = await _load_all_pyq(db, limit, dry_run=dry_run)
            log.info("pyq: %s", results["pyq"])
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
    ap.add_argument("--only", choices=("structure", "pyq", "static_gk"),
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
