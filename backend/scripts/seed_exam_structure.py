"""Seed the Category / SubCategory / ExamStage / ExamPattern structure for every
exam represented in the PYQ corpus at ``~/Documents/pariksha``.

Run from the backend directory::

    python -m scripts.seed_exam_structure

What it creates
---------------
* **Categories (bodies):** Banks, SSC, RRB.
* **SubCategories (exams):** SBI PO, IBPS PO (Banks); CGL, CHSL (SSC); RRB NTPC (RRB).
* **ExamStages + ExamPatterns:** Prelims/Mains (Banks), Tier 1/Tier 2 (SSC),
  CBT 1/CBT 2 (RRB NTPC) — each stage seeded with its section breakdown,
  total Qs, total duration, negative-marking, and sectional-timing flag.

Idempotency
-----------
Re-running the script is safe. Existing rows are fetched by
``(category.name)`` / ``(category_id, slug)`` / ``(subcategory_id, slug)`` and
**left alone** except for the pattern, which is replace-in-place so a revised
blueprint (e.g. updated after a notification change) wins. Critically, the
``is_enabled`` flags on existing rows are **never** touched — once an admin
enables a body/exam/stage, re-seeding won't silently turn it off.

Caveat
------
The patterns here are encoded from the currently-known notifications; exam
boards revise these year to year. When SSC/IBPS publish a new notification,
update the blueprint in ``EXAM_STRUCTURE`` below and re-run.
"""
from __future__ import annotations

import asyncio
import logging
import sys
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.schemas.exam_structure_schema import (
    ExamPatternCreate,
    SectionPatternCreate,
)
from app.services import exam_structure_service as service

log = logging.getLogger("seed_exam_structure")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s | %(message)s")


# --------------------------------------------------------------------------- #
# Blueprint data
# --------------------------------------------------------------------------- #
# The shape mirrors the service layer's creator signatures so we can hand a
# pure-data structure to the seeder and let it walk the tree. Adding a new
# exam = appending a dict; no code changes elsewhere.

EXAM_STRUCTURE: list[dict] = [
    # ------------------------------- BANKS -------------------------------
    # Category name must MATCH the production DB's existing singular form
    # "Bank" — ``ensure_category`` fetches-or-creates by exact name, so using
    # "Banks" here would create a parallel orphan row alongside the existing
    # "Bank" category (which already has 0 subcategories but is referenced by
    # users.selected_exam_category_id). Keep singular.
    {
        "category": {
            "name": "Bank",
            "order": 10,
            "description": (
                "Nationalised-bank probationary-officer and clerk exams — "
                "SBI, IBPS, RBI, etc."
            ),
        },
        "subcategories": [
            {
                "name": "SBI PO",
                "slug": "sbi-po",
                "order": 1,
                "description": "State Bank of India — Probationary Officer recruitment.",
                "stages": [
                    {
                        "name": "Prelims",
                        "slug": "prelims",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=60,
                            total_questions=100,
                            total_marks=100.0,
                            negative_mark_per_wrong=0.25,
                            has_sectional_timing=True,
                            notes=(
                                "Sectional timing enforced. 1/4 negative marking on "
                                "objective questions. Qualifying stage only — marks "
                                "do not count toward final merit."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="English Language",
                                    subject="ENGLISH",
                                    question_count=30,
                                    duration_minutes=20,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="Quantitative Aptitude",
                                    subject="QUANT",
                                    question_count=35,
                                    duration_minutes=20,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="Reasoning Ability",
                                    subject="REASONING",
                                    question_count=35,
                                    duration_minutes=20,
                                    order=3,
                                ),
                            ],
                        ),
                    },
                    {
                        "name": "Mains",
                        "slug": "mains",
                        "order": 2,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=180,
                            total_questions=155,
                            total_marks=200.0,
                            negative_mark_per_wrong=0.25,
                            has_sectional_timing=True,
                            notes=(
                                "Objective + descriptive. Descriptive (Letter + Essay, "
                                "50 marks, 30 min) is a separate paper and not modelled "
                                "here — only the 180-minute objective portion is. "
                                "Sectional timing enforced."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="Reasoning & Computer Aptitude",
                                    subject="REASONING",
                                    question_count=45,
                                    duration_minutes=60,
                                    marks_per_question=1.0,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="Data Analysis & Interpretation",
                                    subject="DATA_INTERPRETATION",
                                    question_count=35,
                                    duration_minutes=45,
                                    marks_per_question=1.0,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="General / Economy / Banking Awareness",
                                    subject="GENERAL_AWARENESS",
                                    question_count=40,
                                    duration_minutes=35,
                                    marks_per_question=1.0,
                                    order=3,
                                ),
                                SectionPatternCreate(
                                    name="English Language",
                                    subject="ENGLISH",
                                    question_count=35,
                                    duration_minutes=40,
                                    marks_per_question=1.0,
                                    order=4,
                                ),
                            ],
                        ),
                    },
                ],
            },
            {
                "name": "IBPS PO",
                "slug": "ibps-po",
                "order": 2,
                "description": "Institute of Banking Personnel Selection — PO / MT.",
                "stages": [
                    {
                        "name": "Prelims",
                        "slug": "prelims",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=60,
                            total_questions=100,
                            total_marks=100.0,
                            negative_mark_per_wrong=0.25,
                            has_sectional_timing=True,
                            notes="Sectional timing 20 min each. Qualifying stage only.",
                            section_patterns=[
                                SectionPatternCreate(
                                    name="English Language",
                                    subject="ENGLISH",
                                    question_count=30,
                                    duration_minutes=20,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="Quantitative Aptitude",
                                    subject="QUANT",
                                    question_count=35,
                                    duration_minutes=20,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="Reasoning Ability",
                                    subject="REASONING",
                                    question_count=35,
                                    duration_minutes=20,
                                    order=3,
                                ),
                            ],
                        ),
                    },
                    {
                        "name": "Mains",
                        "slug": "mains",
                        "order": 2,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=180,
                            total_questions=155,
                            total_marks=200.0,
                            negative_mark_per_wrong=0.25,
                            has_sectional_timing=True,
                            notes=(
                                "Objective portion only (180 min). A separate 30-min "
                                "English descriptive paper exists and is not modelled."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="Reasoning & Computer Aptitude",
                                    subject="REASONING",
                                    question_count=45,
                                    duration_minutes=60,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="English Language",
                                    subject="ENGLISH",
                                    question_count=35,
                                    duration_minutes=40,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="Data Analysis & Interpretation",
                                    subject="DATA_INTERPRETATION",
                                    question_count=35,
                                    duration_minutes=45,
                                    order=3,
                                ),
                                SectionPatternCreate(
                                    name="General / Economy / Banking Awareness",
                                    subject="GENERAL_AWARENESS",
                                    question_count=40,
                                    duration_minutes=35,
                                    order=4,
                                ),
                            ],
                        ),
                    },
                ],
            },
        ],
    },
    # ------------------------------- SSC -------------------------------
    {
        "category": {
            "name": "SSC",
            "order": 20,
            "description": (
                "Staff Selection Commission — CGL, CHSL, MTS, CPO, JE and more."
            ),
        },
        "subcategories": [
            {
                "name": "CGL",
                "slug": "cgl",
                "order": 1,
                "description": "SSC Combined Graduate Level.",
                "stages": [
                    {
                        "name": "Tier 1",
                        "slug": "tier-1",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=60,
                            total_questions=100,
                            total_marks=200.0,
                            negative_mark_per_wrong=0.5,
                            has_sectional_timing=False,
                            notes=(
                                "Each section carries 50 marks (25 Qs × 2 marks). "
                                "PwD candidates get 80 minutes. No sectional timing."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="General Intelligence & Reasoning",
                                    subject="REASONING",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="General Awareness",
                                    subject="GENERAL_AWARENESS",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="Quantitative Aptitude",
                                    subject="QUANT",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=3,
                                ),
                                SectionPatternCreate(
                                    name="English Comprehension",
                                    subject="ENGLISH",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=4,
                                ),
                            ],
                        ),
                    },
                    {
                        "name": "Tier 2",
                        "slug": "tier-2",
                        "order": 2,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=135,
                            total_questions=150,
                            total_marks=450.0,
                            negative_mark_per_wrong=1.0,
                            has_sectional_timing=True,
                            notes=(
                                "Paper 1 only (mandatory for all posts). Paper 2 (Statistics) "
                                "and Paper 3 (Gen Studies — Finance & Economics) are "
                                "post-specific and not modelled. Real-exam timing: "
                                "Section I 60 min (Math + Reasoning, free flow), "
                                "Section II 60 min (English + GA, free flow), "
                                "Section III 15 min (Computer Knowledge, qualifying). "
                                "Per official notification negative marking is 1 mark "
                                "for Section I/II and 0.5 for Section III; we apply a "
                                "uniform 1 mark since the data model carries one rate."
                            ),
                            section_patterns=[
                                # Real exam: Section I is a single 60-min envelope
                                # where the candidate freely allocates time between
                                # Mathematical Abilities (30 Q) and Reasoning (30 Q).
                                # We model it as one section so the sectional timer
                                # behaves like the real paper.
                                SectionPatternCreate(
                                    name="Section I — Math + Reasoning",
                                    subject="MATH_AND_REASONING",
                                    question_count=60,
                                    duration_minutes=60,
                                    marks_per_question=3.0,
                                    order=1,
                                ),
                                # Section II is similarly a single 60-min envelope —
                                # English (45 Q) and General Awareness (25 Q) share
                                # the same timer.
                                SectionPatternCreate(
                                    name="Section II — English + General Awareness",
                                    subject="ENGLISH_AND_GA",
                                    question_count=70,
                                    duration_minutes=60,
                                    marks_per_question=3.0,
                                    order=2,
                                ),
                                # Section III is its own 15-min qualifying module.
                                SectionPatternCreate(
                                    name="Section III — Computer Knowledge",
                                    subject="COMPUTER",
                                    question_count=20,
                                    duration_minutes=15,
                                    marks_per_question=3.0,
                                    order=3,
                                ),
                            ],
                        ),
                    },
                ],
            },
            {
                "name": "CHSL",
                "slug": "chsl",
                "order": 2,
                "description": "SSC Combined Higher Secondary Level (10+2).",
                "stages": [
                    {
                        "name": "Tier 1",
                        "slug": "tier-1",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=60,
                            total_questions=100,
                            total_marks=200.0,
                            negative_mark_per_wrong=0.5,
                            has_sectional_timing=False,
                            notes="Each section 25 Qs × 2 marks. PwD gets 80 min.",
                            section_patterns=[
                                SectionPatternCreate(
                                    name="English Language",
                                    subject="ENGLISH",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="General Awareness",
                                    subject="GENERAL_AWARENESS",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="Quantitative Aptitude",
                                    subject="QUANT",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=3,
                                ),
                                SectionPatternCreate(
                                    name="General Intelligence",
                                    subject="REASONING",
                                    question_count=25,
                                    marks_per_question=2.0,
                                    order=4,
                                ),
                            ],
                        ),
                    },
                    {
                        "name": "Tier 2",
                        "slug": "tier-2",
                        "order": 2,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=135,
                            total_questions=135,
                            total_marks=405.0,
                            negative_mark_per_wrong=1.0,
                            has_sectional_timing=True,
                            notes=(
                                "Real-exam timing: Section I 60 min (Math + Reasoning, "
                                "free flow), Section II 60 min (English + GA, free flow), "
                                "Section III 15 min (Computer Knowledge, qualifying). "
                                "Section III is qualifying-only and uses 0.5 negative "
                                "marking per wrong; the data model carries a single rate "
                                "so we apply a uniform 1.0."
                            ),
                            section_patterns=[
                                # Single 60-min envelope. Math 30 + Reasoning 30 share
                                # the same timer so the candidate can flow freely.
                                SectionPatternCreate(
                                    name="Section I — Math + Reasoning",
                                    subject="MATH_AND_REASONING",
                                    question_count=60,
                                    duration_minutes=60,
                                    marks_per_question=3.0,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="Section II — English + General Awareness",
                                    subject="ENGLISH_AND_GA",
                                    question_count=60,
                                    duration_minutes=60,
                                    marks_per_question=3.0,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="Section III — Computer Knowledge",
                                    subject="COMPUTER",
                                    question_count=15,
                                    duration_minutes=15,
                                    marks_per_question=3.0,
                                    order=3,
                                ),
                            ],
                        ),
                    },
                ],
            },
        ],
    },
    # ------------------------------- RAILWAY (RRB) -----------------------
    # Production DB uses "Railway" (not "RRB") as the category name; keep
    # that so we reuse the existing row instead of creating a duplicate.
    {
        "category": {
            "name": "Railway",
            "order": 30,
            "description": "Railway Recruitment Board — NTPC, Group D, JE, ALP.",
        },
        "subcategories": [
            {
                "name": "RRB NTPC",
                "slug": "ntpc",
                "order": 1,
                "description": (
                    "Non-Technical Popular Categories — graduate and undergraduate "
                    "level posts."
                ),
                "stages": [
                    {
                        "name": "CBT 1",
                        "slug": "cbt-1",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=90,
                            total_questions=100,
                            total_marks=100.0,
                            negative_mark_per_wrong=0.3333,
                            has_sectional_timing=False,
                            notes=(
                                "1/3 negative marking. PwD candidates get 120 minutes. "
                                "Screening stage."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="General Awareness",
                                    subject="GENERAL_AWARENESS",
                                    question_count=40,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="Mathematics",
                                    subject="QUANT",
                                    question_count=30,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="General Intelligence & Reasoning",
                                    subject="REASONING",
                                    question_count=30,
                                    order=3,
                                ),
                            ],
                        ),
                    },
                    {
                        "name": "CBT 2",
                        "slug": "cbt-2",
                        "order": 2,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=90,
                            total_questions=120,
                            total_marks=120.0,
                            negative_mark_per_wrong=0.3333,
                            has_sectional_timing=False,
                            notes="Graduate level. 1/3 negative marking. PwD 120 min.",
                            section_patterns=[
                                SectionPatternCreate(
                                    name="General Awareness",
                                    subject="GENERAL_AWARENESS",
                                    question_count=50,
                                    order=1,
                                ),
                                SectionPatternCreate(
                                    name="Mathematics",
                                    subject="QUANT",
                                    question_count=35,
                                    order=2,
                                ),
                                SectionPatternCreate(
                                    name="General Intelligence & Reasoning",
                                    subject="REASONING",
                                    question_count=35,
                                    order=3,
                                ),
                            ],
                        ),
                    },
                ],
            },
        ],
    },
    # ------------------------------- UPSC (EPFO) -------------------------
    {
        "category": {
            "name": "UPSC",
            "order": 40,
            "description": (
                "Union Public Service Commission — EPFO APFC, EO/AO and other "
                "central services recruitment tests."
            ),
        },
        "subcategories": [
            {
                "name": "EPFO APFC",
                "slug": "epfo-apfc",
                "order": 1,
                "description": (
                    "Employees' Provident Fund Organisation — Assistant Provident "
                    "Fund Commissioner recruitment test."
                ),
                "stages": [
                    {
                        "name": "Recruitment Test",
                        "slug": "recruitment-test",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=120,
                            total_questions=120,
                            total_marks=300.0,
                            negative_mark_per_wrong=0.8333,
                            has_sectional_timing=False,
                            notes=(
                                "Single paper, 120 MCQs, 2 hours. Marks: +2.5 per "
                                "correct, -0.833 per wrong (1/3 negative marking). "
                                "No sectional timing. Covers English, General Studies, "
                                "Labour Laws, Social Security, Accounting, Polity, "
                                "History, Science, Mathematics, and Current Affairs."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="General Studies & Social Security",
                                    subject="GENERAL_STUDIES",
                                    question_count=120,
                                    duration_minutes=120,
                                    marks_per_question=2.5,
                                    order=1,
                                ),
                            ],
                        ),
                    },
                ],
            },
            {
                "name": "EPFO EO/AO",
                "slug": "epfo-eo-ao",
                "order": 2,
                "description": (
                    "Employees' Provident Fund Organisation — Enforcement Officer / "
                    "Accounts Officer recruitment test."
                ),
                "stages": [
                    {
                        "name": "Recruitment Test",
                        "slug": "recruitment-test",
                        "order": 1,
                        "pattern": ExamPatternCreate(
                            total_duration_minutes=120,
                            total_questions=120,
                            total_marks=300.0,
                            negative_mark_per_wrong=0.8333,
                            has_sectional_timing=False,
                            notes=(
                                "Single paper, 120 MCQs, 2 hours. Same pattern as APFC. "
                                "Marks: +2.5 per correct, -0.833 per wrong. "
                                "2025 onwards APFC and EO/AO share the same paper."
                            ),
                            section_patterns=[
                                SectionPatternCreate(
                                    name="General Studies & Social Security",
                                    subject="GENERAL_STUDIES",
                                    question_count=120,
                                    duration_minutes=120,
                                    marks_per_question=2.5,
                                    order=1,
                                ),
                            ],
                        ),
                    },
                ],
            },
        ],
    },
]


# --------------------------------------------------------------------------- #
# Seeder
# --------------------------------------------------------------------------- #

async def seed(db: AsyncSession, blueprint: Sequence[dict]) -> None:
    summary = {"categories": 0, "subcategories": 0, "stages": 0, "patterns": 0}
    for body in blueprint:
        cat_meta = body["category"]
        cat = await service.ensure_category(
            db,
            name=cat_meta["name"],
            order=cat_meta.get("order", 0),
            description=cat_meta.get("description"),
        )
        summary["categories"] += 1
        log.info("Category %-8s ✓  id=%s  enabled=%s", cat.name, cat.id, cat.is_enabled)

        for sub_meta in body["subcategories"]:
            sub = await service.ensure_subcategory(
                db,
                category=cat,
                name=sub_meta["name"],
                slug=sub_meta["slug"],
                order=sub_meta.get("order", 0),
                description=sub_meta.get("description"),
            )
            summary["subcategories"] += 1
            log.info(
                "  SubCategory %-10s ✓  id=%s  enabled=%s", sub.name, sub.id, sub.is_enabled
            )

            for stage_meta in sub_meta["stages"]:
                pattern: ExamPatternCreate | None = stage_meta.get("pattern")
                if pattern is not None:
                    service.validate_pattern_sums(pattern)
                stage = await service.ensure_exam_stage_with_pattern(
                    db,
                    subcategory=sub,
                    name=stage_meta["name"],
                    slug=stage_meta["slug"],
                    order=stage_meta.get("order", 0),
                    pattern=pattern,
                )
                summary["stages"] += 1
                if pattern is not None:
                    summary["patterns"] += 1
                log.info(
                    "    Stage %-8s ✓  id=%s  enabled=%s  pattern=%s",
                    stage.name,
                    stage.id,
                    stage.is_enabled,
                    "yes" if pattern else "no",
                )

    await db.commit()
    log.info("Seed complete. %s", summary)


async def main() -> int:
    async with SessionLocal() as db:
        try:
            await seed(db, EXAM_STRUCTURE)
        except Exception:
            await db.rollback()
            log.exception("Seed failed — transaction rolled back.")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
