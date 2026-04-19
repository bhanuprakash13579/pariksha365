"""Pydantic schemas for the post-attempt personalised feedback engine.

The engine returns one :class:`FeedbackReport` per attempt that the frontend
renders as the student's scorecard + action plan. See
``memory: project_personalized_feedback_engine`` for the full product spec;
see ``memory: feedback_time_to_marks_efficiency`` for the Tier A/B/C rule
that drives ``priority_score``.

Design decisions worth knowing:

* All numeric fields use plain ``int`` / ``float`` — no decimals, no enums
  beyond what's necessary, because the frontend renders directly without a
  mapping layer.
* Each ``Recommendation`` is self-contained: the UI can render the top-N
  without looking anything else up. This is what ``study_shortcut`` is for.
* ``PerformanceBucket`` (weak/intermediate/advanced) is derived from
  overall accuracy thresholds in the service — kept out of this schema so
  the UI never makes that decision.
"""
from __future__ import annotations

from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


PerformanceBucket = Literal["weak", "intermediate", "advanced"]
EffortTier = Literal["A", "B", "C"]


class TopicBreakdown(BaseModel):
    """Per-topic accuracy + timing + marks-at-stake."""
    subject: str
    topic: Optional[str] = None
    topic_code: Optional[str] = None
    effort_tier: Optional[EffortTier] = None
    attempted: int
    correct: int
    incorrect: int
    skipped: int
    accuracy_pct: float
    avg_time_seconds: float
    # Marks actually scored / maximum possible on this topic in the attempt
    marks_scored: float
    marks_possible: float
    marks_lost: float
    # Raw bucket counts of pace
    fast_and_right: int = 0       # correct + faster than benchmark
    slow_and_right: int = 0       # correct but slower than benchmark
    fast_and_wrong: int = 0       # wrong + fast (careless error)
    slow_and_wrong: int = 0       # wrong + slow (concept gap)


class SectionBreakdown(BaseModel):
    """Section-level view used to spot time-budget issues."""
    name: str
    subject: str
    question_count: int
    attempted: int
    correct: int
    time_spent_seconds: int
    time_budget_seconds: Optional[int] = None  # from ExamPattern.SectionPattern if present
    time_budget_used_pct: Optional[float] = None
    accuracy_pct: float
    marks_scored: float
    marks_possible: float


class Recommendation(BaseModel):
    """One actionable priority the student should act on next.

    Ordered by ``priority_score``; the top 3-5 render on the scorecard. The
    UI should render ``study_shortcut`` verbatim — it came from the
    ``_syllabus/*.json`` files' curated guidance.
    """
    rank: int
    topic: str
    topic_code: Optional[str] = None
    subject: str
    effort_tier: EffortTier
    marks_lost: float
    estimated_marks_lift: float
    priority_score: float
    kind: Literal[
        "topic_priority",     # "Practice X; you lost 6 marks here"
        "speed_drill",        # "Slow on DI; drill against a 2-min timer"
        "concept_gap",        # "Missed EASY Qs — revise basics"
        "guessing_hygiene",   # "You guessed and lost 4 marks to negatives"
        "time_budget",        # "You rushed English; used 11/20 min"
        "high_weight_nudge",  # "Polity gives 18 marks; you got 8"
    ]
    headline: str             # single-line pitch shown as row title
    detail: str               # 1-2 sentence supporting text
    study_shortcut: Optional[str] = None
    practice_launch: Optional[dict] = None  # payload the "Practice Now" button posts


class DiagnosticSignal(BaseModel):
    """Aggregate signals that feed the UI's secondary panels."""
    overall_accuracy_pct: float
    overall_attempted_pct: float
    marks_scored: float
    marks_possible: float
    marks_lost_to_negative: float
    net_score: float
    performance_bucket: PerformanceBucket
    trend_vs_last_attempt: Optional[float] = None  # +/- percentage points
    best_topic: Optional[str] = None
    worst_topic: Optional[str] = None


class FeedbackReport(BaseModel):
    """Full report the frontend renders as the post-attempt scorecard."""
    attempt_id: UUID
    exam_slug: Optional[str] = None
    stage_slug: Optional[str] = None
    generated_at: str                         # ISO8601 UTC
    diagnostic: DiagnosticSignal
    sections: List[SectionBreakdown]
    topics: List[TopicBreakdown]              # all topics, ordered worst→best
    recommendations: List[Recommendation]     # ordered by priority_score desc
    efficiency_pitch: Optional[str] = None    # verbatim from high_weight_topics.json

    model_config = ConfigDict(from_attributes=True)
