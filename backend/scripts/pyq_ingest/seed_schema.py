"""Canonical on-disk seed schema.

This is the single contract shared by three producers — the PYQ ingester
(Phase 2b), the mock-test generator (Phase 3), and the static-GK writer
(Phase 3b) — and one consumer, the DB loader (Phase LOAD) that turns these
files into ``TestSeries`` / ``Section`` / ``Question`` / ``QuizQuestion`` rows.

Layout on disk (under ``backend/seeds/``)::

    seeds/
      pyq/<body>/<exam>/<stage>/<pdf-stem>.json   # one per PYQ PDF
      pyq/_index.json                              # flat listing of all PYQ papers
      mocks/<body>/<exam>/<stage>/mock-NN.json    # generated mocks
      static_gk/<subject>/<topic>.json             # static-GK bundles
      images/<sha1>/page-N-img-M.<ext>             # extracted per-PDF images

Keeping the schema here (not in ``app/schemas``) so the ingester can run
independently of a DB connection, and so loader compatibility is a pure
data-validation concern — you can inspect a seed file without booting the
app.

Every question record carries a **deterministic id** derived from its
provenance (source PDF + printed number for PYQs; topic + index for generated
content), so re-running an ingester never creates duplicate rows on reload.
"""
from __future__ import annotations

from datetime import date
from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field

SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- #
# Tags and enums
# --------------------------------------------------------------------------- #

AnswerSource = Literal[
    "pdf_extracted",   # parsed from the PYQ PDF's answer key (color or S<N>.Ans)
    "generated",       # produced by Claude-in-chat at build time
    "manual_admin",    # admin entered via the panel
]

StalenessRisk = Literal[
    0,  # pure static — permanent fact, will never decay
    1,  # gray area — static today but might shift (banking rates-ish concepts)
    2,  # current affairs — excluded from mocks and practice pool entirely
]

TestType = Literal["PYQ", "MOCK"]


# --------------------------------------------------------------------------- #
# Building blocks
# --------------------------------------------------------------------------- #

class QuestionImage(BaseModel):
    """An image attached to a question (extracted from the source PDF or
    produced fresh at generation time)."""

    path: str                           # relative to seeds/ root, e.g. "images/abc/p3-img1.png"
    width: Optional[int] = None
    height: Optional[int] = None
    alt: Optional[str] = None           # human description when the generator can provide one


class SeedQuestion(BaseModel):
    """One question in its canonical, DB-ready form."""

    id: str                             # deterministic — see _build_question_id in seed_writer.py
    stem: str
    passage_context: Optional[str] = None  # shared passage for Directions-based Qs; renders above stem
    options: List[str]                  # 2-5 entries in display order
    correct_index: Optional[int] = None # 0-based
    correct_letter: Optional[str] = None
    explanation: Optional[str] = None
    subject: str                        # canonical key: REASONING/QUANT/ENGLISH/...
    topic: Optional[str] = None         # sub-topic label e.g. "percentage"
    topic_code: Optional[str] = None    # deterministic key e.g. "QNT_PCT" for weak-topic matcher
    difficulty: Literal["EASY", "MEDIUM", "HARD"] = "MEDIUM"
    answer_source: AnswerSource = "pdf_extracted"
    staleness_risk: StalenessRisk = 0
    images: List[QuestionImage] = Field(default_factory=list)
    # Provenance (populated for PYQs, empty for generated content)
    source_pdf_path: Optional[str] = None     # relative to corpus root
    source_page_range: Optional[List[int]] = None  # [start, end] 1-based pages
    printed_number: Optional[int] = None
    parse_issues: List[str] = Field(default_factory=list)

    model_config = ConfigDict(extra="forbid")


class SeedSection(BaseModel):
    """A section under a test series — maps 1:1 to the ``sections`` DB table."""

    name: str
    subject: str                        # canonical subject key
    order: int
    time_limit_minutes: Optional[int] = None
    marks_per_question: float = 1.0
    questions: List[SeedQuestion]

    model_config = ConfigDict(extra="forbid")


class SeedTestSeries(BaseModel):
    """A single test series (one PYQ paper, one generated mock, …). Maps 1:1
    to the ``test_series`` DB table, with its ``sections`` and their
    ``questions`` embedded so the loader can insert atomically.
    """

    schema_version: int = SCHEMA_VERSION
    id: str                             # deterministic (slug-based)
    title: str
    description: Optional[str] = None
    test_type: TestType
    # Hierarchical placement — loader will resolve these slugs against the
    # exam-structure tables seeded in Phase 1e.
    body_slug: str                      # "banks", "ssc", "rrb"
    exam_slug: str                      # "sbi-po", "cgl", ...
    stage_slug: str                     # "prelims", "tier-1", ...
    # Official timing/scoring derived from the ExamPattern; loader can cross-check.
    total_duration_minutes: int
    negative_marking: float = 0.0
    has_sectional_timing: bool = False
    # PYQ provenance (empty for MOCK)
    source_pdf_path: Optional[str] = None
    source_format: Optional[str] = None
    paper_date: Optional[date] = None
    paper_shift: Optional[str] = None
    # Parse health (populated by ingester, informational for loader)
    parse_health: dict = Field(default_factory=dict)
    sections: List[SeedSection]

    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- #
# Static-GK bundle
# --------------------------------------------------------------------------- #

class SeedStaticGKBundle(BaseModel):
    """A file in ``seeds/static_gk/<subject>/<topic>.json`` — many questions
    sharing the same subject + topic, written by the generator in batches.
    These map to rows in the ``quiz_questions`` table at load time (not to
    ``test_series``).
    """

    schema_version: int = SCHEMA_VERSION
    subject: str
    topic: str
    topic_code: str
    description: Optional[str] = None
    questions: List[SeedQuestion]

    model_config = ConfigDict(extra="forbid")


# --------------------------------------------------------------------------- #
# Index files
# --------------------------------------------------------------------------- #

class SeedIndexEntry(BaseModel):
    file: str                           # relative path to the JSON
    title: str
    test_type: TestType
    body_slug: str
    exam_slug: str
    stage_slug: str
    questions: int

    model_config = ConfigDict(extra="forbid")


class SeedIndex(BaseModel):
    schema_version: int = SCHEMA_VERSION
    generated_at: str                   # ISO8601
    entries: List[SeedIndexEntry]

    model_config = ConfigDict(extra="forbid")
