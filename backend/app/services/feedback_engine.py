"""Personalised feedback engine — turns one ``Attempt`` into a
:class:`FeedbackReport` the student reads after submitting.

Why it exists
-------------

The existing analytics service computes subject-level accuracy and returns
it to the student verbatim. Students don't know what to do with "You got
62 % in Quant." This service goes further:

1. Per-topic accuracy × time × mark-share × effort-tier → a single
   **priority_score** that ranks what to study next.
2. Pace buckets (fast+right / slow+right / fast+wrong / slow+wrong) that
   surface *why* a topic went badly — concept gap vs careless error vs
   time pressure.
3. High-weight and efficiency-tier metadata pulled from
   ``seeds/_analysis/high_weight_topics.json`` so the recommendations
   include a verbatim ``study_shortcut`` ("Daily 20-Q BODMAS drill …") and
   honour the weak-student-first-Tier-A rule from
   ``memory: feedback_time_to_marks_efficiency``.
4. A full per-section time-budget view so students who rushed / over-spent
   get flagged directly.

The caller loads an ``Attempt`` with its answers/questions/sections and
passes it in; the service returns a ready-to-serialise :class:`FeedbackReport`.

Key design choices
------------------

* **Pure computation, no DB writes.** This keeps the engine testable and
  lets the router decide whether to cache or persist the report later.
* **Registry loaded once per process** (``@lru_cache``). The JSON is small
  (~30 KB) but parsing it per-request would be wasteful.
* **Graceful degradation.** If a topic lacks a registry entry (e.g. the
  mock uses a topic_code we haven't classified yet), the engine falls back
  to defaults rather than erroring — the student still gets a score, just
  with less tailored guidance.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
from uuid import UUID

from app.models.attempt import Attempt
from app.schemas.feedback_schema import (
    DiagnosticSignal,
    EffortTier,
    FeedbackReport,
    PerformanceBucket,
    Recommendation,
    SectionBreakdown,
    TopicBreakdown,
)

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Tunables
# --------------------------------------------------------------------------- #

# Thresholds on overall accuracy for bucketing.
_BUCKET_THRESHOLDS = {"weak": 0.50, "intermediate": 0.75}

# Effort-tier multiplier when ranking recommendations — lifted directly from
# the registry's ``effort_multipliers`` block so both systems agree.
_TIER_MULTIPLIERS: Dict[str, float] = {"A": 3.0, "B": 1.5, "C": 0.7}

# Default speed benchmarks (seconds/Q) used when the registry has none.
_SPEED_DEFAULTS = {"ENGLISH": 40, "QUANT": 55, "REASONING": 45, "GENERAL_AWARENESS": 25, "COMPUTER": 30, "DATA_INTERPRETATION": 90}

_REGISTRY_PATH = Path(__file__).resolve().parents[2] / "seeds" / "_analysis" / "high_weight_topics.json"


# --------------------------------------------------------------------------- #
# Registry loader
# --------------------------------------------------------------------------- #

@lru_cache(maxsize=1)
def _load_registry() -> dict:
    """Parse ``high_weight_topics.json`` once per process. Returns an empty
    dict if the file is missing (e.g. in a fresh deployment before the
    registry has been built) — the engine still works, just without tier
    bonuses or study-shortcut strings.
    """
    try:
        return json.loads(_REGISTRY_PATH.read_text())
    except FileNotFoundError:
        log.warning("feedback registry missing at %s — running with defaults", _REGISTRY_PATH)
        return {"registry": {}}


def _tier_for_topic(
    registry_entry: Optional[dict], topic_code: Optional[str], subject: str
) -> EffortTier:
    """Resolve the Tier (A/B/C) of a topic for this exam/stage, with
    sensible fallback to 'B' when unknown.

    We look inside the per-exam ``high_weight_topics`` list first (that's
    the authoritative per-exam tiering), then walk the full syllabus JSON
    later if needed. For simplicity v1 only consults the registry; future
    iterations can layer syllabus-file lookup on top.
    """
    if registry_entry and topic_code:
        for hw in registry_entry.get("high_weight_topics", []):
            if hw.get("topic_code") == topic_code:
                return hw.get("effort_tier") or "B"
    return "B"


def _study_shortcut(
    registry_entry: Optional[dict], topic_code: Optional[str]
) -> Optional[str]:
    if registry_entry and topic_code:
        for hw in registry_entry.get("high_weight_topics", []):
            if hw.get("topic_code") == topic_code and hw.get("study_shortcut"):
                return hw["study_shortcut"]
    return None


# --------------------------------------------------------------------------- #
# Core computation
# --------------------------------------------------------------------------- #

def _is_correct(question, selected_idx: Optional[int]) -> bool:
    if selected_idx is None:
        return False
    opts = getattr(question, "options", None) or []
    if not (0 <= selected_idx < len(opts)):
        return False
    opt = opts[selected_idx]
    if isinstance(opt, dict):
        return bool(opt.get("is_correct"))
    return False


def _marks_for(question, section, was_correct: bool, was_skipped: bool, neg_mark: float) -> float:
    """Marks contribution of this answer to the student's net score.
    Skipped questions score 0; wrong answers apply negative marking.
    """
    per_q = 1.0
    if section is not None:
        per_q = float(getattr(section, "marks_per_question", None) or 1.0)
    if was_skipped:
        return 0.0
    if was_correct:
        return per_q
    return -neg_mark


def _bucket(overall_acc: float) -> PerformanceBucket:
    if overall_acc < _BUCKET_THRESHOLDS["weak"]:
        return "weak"
    if overall_acc < _BUCKET_THRESHOLDS["intermediate"]:
        return "intermediate"
    return "advanced"


def _pace_bucket(was_correct: bool, was_skipped: bool, time_s: int, benchmark_s: int) -> str:
    if was_skipped:
        return "skipped"
    fast = time_s <= benchmark_s
    if was_correct and fast:
        return "fast_and_right"
    if was_correct and not fast:
        return "slow_and_right"
    if (not was_correct) and fast:
        return "fast_and_wrong"
    return "slow_and_wrong"


def build_feedback_report(
    attempt: Attempt,
    *,
    exam_slug: Optional[str] = None,
    stage_slug: Optional[str] = None,
    negative_mark: Optional[float] = None,
    previous_attempt_accuracy: Optional[float] = None,
) -> FeedbackReport:
    """Turn an ``Attempt`` (with its sections, questions, user_answers loaded)
    into a ready-to-serve :class:`FeedbackReport`.

    Caller must ensure the ORM graph is eager-loaded: ``attempt.user_answers
    -> .question -> .section -> .test_series`` for marks-per-Q and section
    time budgets.
    """
    registry = _load_registry().get("registry", {})
    key = f"{exam_slug}__{stage_slug}" if exam_slug and stage_slug else None
    registry_entry = registry.get(key) if key else None
    neg_mark = negative_mark if negative_mark is not None else float(
        getattr(attempt.test_series, "negative_marking", None) or 0.0
    )

    # --- Group answers by section (for section breakdown + budget check) ---
    sections_map: Dict[str, dict] = {}
    topics_map: Dict[Tuple[str, Optional[str]], dict] = {}  # (subject, topic_code)

    marks_scored = 0.0
    marks_possible = 0.0
    marks_lost_to_neg = 0.0
    correct_total = 0
    attempted_total = 0
    answer_count = 0

    for ans in (attempt.user_answers or []):
        q = ans.question
        if q is None:
            continue
        sec = getattr(q, "section", None)
        subject = q.subject or "General"
        topic = q.topic
        topic_code = q.topic_code
        time_s = int(ans.time_spent_seconds or 0)
        selected = ans.selected_option_index
        was_skipped = selected is None
        was_correct = _is_correct(q, selected)
        m = _marks_for(q, sec, was_correct, was_skipped, neg_mark)
        per_q = float(getattr(sec, "marks_per_question", None) or 1.0)

        answer_count += 1
        marks_possible += per_q
        marks_scored += max(0.0, m) if was_correct else 0.0
        if (not was_correct) and (not was_skipped):
            marks_lost_to_neg += neg_mark
        if not was_skipped:
            attempted_total += 1
            if was_correct:
                correct_total += 1

        # Section rollup
        sec_key = getattr(sec, "id", None) or subject
        if sec_key not in sections_map:
            sections_map[sec_key] = {
                "name": getattr(sec, "name", None) or subject,
                "subject": subject,
                "question_count": 0,
                "attempted": 0,
                "correct": 0,
                "time_spent_seconds": 0,
                "time_budget_seconds": (int(getattr(sec, "time_limit_minutes", 0) or 0) * 60) or None,
                "marks_scored": 0.0,
                "marks_possible": 0.0,
            }
        srec = sections_map[sec_key]
        srec["question_count"] += 1
        srec["time_spent_seconds"] += time_s
        srec["marks_possible"] += per_q
        if not was_skipped:
            srec["attempted"] += 1
            if was_correct:
                srec["correct"] += 1
                srec["marks_scored"] += per_q

        # Topic rollup
        tkey = (subject, topic_code)
        if tkey not in topics_map:
            topics_map[tkey] = {
                "subject": subject,
                "topic": topic,
                "topic_code": topic_code,
                "attempted": 0,
                "correct": 0,
                "incorrect": 0,
                "skipped": 0,
                "time": 0,
                "marks_scored": 0.0,
                "marks_possible": 0.0,
                "marks_lost": 0.0,
                "fast_and_right": 0,
                "slow_and_right": 0,
                "fast_and_wrong": 0,
                "slow_and_wrong": 0,
            }
        trec = topics_map[tkey]
        trec["time"] += time_s
        trec["marks_possible"] += per_q
        benchmark = _SPEED_DEFAULTS.get(subject, 45)
        pace = _pace_bucket(was_correct, was_skipped, time_s, benchmark)
        if was_skipped:
            trec["skipped"] += 1
            trec["marks_lost"] += per_q  # didn't score it, so lost it
        else:
            trec["attempted"] += 1
            if was_correct:
                trec["correct"] += 1
                trec["marks_scored"] += per_q
                trec[pace] = trec.get(pace, 0) + 1
            else:
                trec["incorrect"] += 1
                trec["marks_lost"] += per_q + neg_mark
                trec[pace] = trec.get(pace, 0) + 1

    # --- Finalise breakdowns ------------------------------------------------
    total_qs = answer_count or 1
    overall_acc = correct_total / total_qs if total_qs else 0.0
    bucket = _bucket(overall_acc)

    section_breakdowns: List[SectionBreakdown] = []
    for sr in sections_map.values():
        budget = sr["time_budget_seconds"]
        used_pct = (
            round(100.0 * sr["time_spent_seconds"] / budget, 1)
            if budget and budget > 0 else None
        )
        acc = 100.0 * sr["correct"] / sr["question_count"] if sr["question_count"] else 0.0
        section_breakdowns.append(SectionBreakdown(
            name=sr["name"],
            subject=sr["subject"],
            question_count=sr["question_count"],
            attempted=sr["attempted"],
            correct=sr["correct"],
            time_spent_seconds=sr["time_spent_seconds"],
            time_budget_seconds=budget,
            time_budget_used_pct=used_pct,
            accuracy_pct=round(acc, 1),
            marks_scored=round(sr["marks_scored"], 2),
            marks_possible=round(sr["marks_possible"], 2),
        ))

    topic_breakdowns: List[TopicBreakdown] = []
    for tr in topics_map.values():
        total = tr["attempted"] + tr["skipped"]
        acc = 100.0 * tr["correct"] / total if total else 0.0
        avg_t = tr["time"] / total if total else 0.0
        tier = _tier_for_topic(registry_entry, tr["topic_code"], tr["subject"])
        topic_breakdowns.append(TopicBreakdown(
            subject=tr["subject"],
            topic=tr["topic"],
            topic_code=tr["topic_code"],
            effort_tier=tier,
            attempted=tr["attempted"],
            correct=tr["correct"],
            incorrect=tr["incorrect"],
            skipped=tr["skipped"],
            accuracy_pct=round(acc, 1),
            avg_time_seconds=round(avg_t, 1),
            marks_scored=round(tr["marks_scored"], 2),
            marks_possible=round(tr["marks_possible"], 2),
            marks_lost=round(tr["marks_lost"], 2),
            fast_and_right=tr["fast_and_right"],
            slow_and_right=tr["slow_and_right"],
            fast_and_wrong=tr["fast_and_wrong"],
            slow_and_wrong=tr["slow_and_wrong"],
        ))
    # Worst-first for UI rendering
    topic_breakdowns.sort(key=lambda t: (-t.marks_lost, t.accuracy_pct))

    # --- Recommendations ----------------------------------------------------
    recs = _build_recommendations(
        topic_breakdowns, section_breakdowns, registry_entry,
        bucket, marks_lost_to_neg,
    )

    # --- Diagnostic ---------------------------------------------------------
    best = min(topic_breakdowns, key=lambda t: -t.accuracy_pct) if topic_breakdowns else None
    worst = topic_breakdowns[0] if topic_breakdowns else None
    trend = None
    if previous_attempt_accuracy is not None:
        trend = round((overall_acc * 100.0) - previous_attempt_accuracy, 1)

    diag = DiagnosticSignal(
        overall_accuracy_pct=round(100.0 * overall_acc, 1),
        overall_attempted_pct=round(100.0 * attempted_total / total_qs, 1),
        marks_scored=round(marks_scored, 2),
        marks_possible=round(marks_possible, 2),
        marks_lost_to_negative=round(marks_lost_to_neg, 2),
        net_score=round(marks_scored - marks_lost_to_neg, 2),
        performance_bucket=bucket,
        trend_vs_last_attempt=trend,
        best_topic=best.topic if best else None,
        worst_topic=worst.topic if worst else None,
    )

    return FeedbackReport(
        attempt_id=attempt.id,
        exam_slug=exam_slug,
        stage_slug=stage_slug,
        generated_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
        diagnostic=diag,
        sections=section_breakdowns,
        topics=topic_breakdowns,
        recommendations=recs,
        efficiency_pitch=(registry_entry or {}).get("efficiency_pitch"),
    )


# --------------------------------------------------------------------------- #
# Recommendation builder
# --------------------------------------------------------------------------- #

def _build_recommendations(
    topics: List[TopicBreakdown],
    sections: List[SectionBreakdown],
    registry_entry: Optional[dict],
    bucket: PerformanceBucket,
    marks_lost_to_neg: float,
) -> List[Recommendation]:
    """Score topics by (marks_lost × tier_multiplier) and render up to five
    actionable rows, plus section-level signals that always deserve a row
    when they trip (rushing a section, guessing recklessly, missing easy
    Qs, etc.).
    """
    scored: List[Tuple[float, TopicBreakdown]] = []
    for t in topics:
        if t.attempted + t.skipped == 0:
            continue
        mult = _TIER_MULTIPLIERS.get(t.effort_tier or "B", 1.0)
        # Weak students should see Tier A first even if marks_lost is modest;
        # advanced students benefit more from tackling Tier C topics where
        # they plateau.
        bucket_boost = 1.0
        if bucket == "weak" and t.effort_tier == "A":
            bucket_boost = 1.25
        elif bucket == "advanced" and t.effort_tier == "C":
            bucket_boost = 1.15
        score = t.marks_lost * mult * bucket_boost
        scored.append((score, t))
    scored.sort(key=lambda pair: -pair[0])

    recs: List[Recommendation] = []
    rank = 0

    # Top topic priorities
    for score, t in scored[:5]:
        if score <= 0.5:
            break  # don't fill with cosmetic rows
        rank += 1
        est_lift = round(t.marks_lost * 0.6, 2)  # conservative: expect to recover 60 %
        kind = "topic_priority"
        headline = f"{t.topic or t.subject} — you lost {t.marks_lost:.1f} marks here"
        detail_bits: List[str] = []
        # Pace-based framing
        if t.slow_and_wrong and t.slow_and_wrong >= t.incorrect / 2:
            kind = "concept_gap"
            detail_bits.append(f"Slow-and-wrong on {t.slow_and_wrong} Qs → underlying concept needs revision.")
        elif t.fast_and_wrong >= 2:
            kind = "concept_gap" if t.slow_and_wrong else "guessing_hygiene"
            detail_bits.append(f"Fast-and-wrong on {t.fast_and_wrong} Qs → likely careless errors or guesses.")
        elif t.slow_and_right and t.slow_and_right >= 3:
            kind = "speed_drill"
            detail_bits.append(f"Correct but slow on {t.slow_and_right} Qs → drill against a timer to save minutes.")
        if t.effort_tier == "A":
            detail_bits.append("Tier A topic — high marks-per-hour ROI.")
        elif t.effort_tier == "C":
            detail_bits.append("Tier C topic — large time investment; only prioritise if you're aiming for a top rank.")
        recs.append(Recommendation(
            rank=rank,
            topic=t.topic or t.subject,
            topic_code=t.topic_code,
            subject=t.subject,
            effort_tier=t.effort_tier or "B",
            marks_lost=t.marks_lost,
            estimated_marks_lift=est_lift,
            priority_score=round(score, 2),
            kind=kind,
            headline=headline,
            detail=" ".join(detail_bits) or f"Practice {t.topic or t.subject} questions to close this gap.",
            study_shortcut=_study_shortcut(registry_entry, t.topic_code),
            practice_launch={"subject": t.subject, "topic_code": t.topic_code} if t.topic_code else None,
        ))

    # Section time-budget signal
    for s in sections:
        if s.time_budget_used_pct is None:
            continue
        if s.time_budget_used_pct < 60 and s.attempted < s.question_count * 0.75:
            rank += 1
            recs.append(Recommendation(
                rank=rank,
                topic=s.name,
                topic_code=None,
                subject=s.subject,
                effort_tier="B",
                marks_lost=round(s.marks_possible - s.marks_scored, 2),
                estimated_marks_lift=round((s.marks_possible - s.marks_scored) * 0.4, 2),
                priority_score=round((s.marks_possible - s.marks_scored) * 1.5, 2),
                kind="time_budget",
                headline=f"You rushed {s.name} — used only {s.time_budget_used_pct:.0f}% of section time",
                detail=(
                    f"Only attempted {s.attempted}/{s.question_count} Qs. Easy marks likely "
                    "left on the table. Plan to use the full sectional window next time."
                ),
            ))
            break  # only one time-budget row

    # Guessing hygiene
    if marks_lost_to_neg >= 3.0:
        rank += 1
        recs.append(Recommendation(
            rank=rank,
            topic="Guessing hygiene",
            topic_code=None,
            subject="GENERAL",
            effort_tier="A",
            marks_lost=round(marks_lost_to_neg, 2),
            estimated_marks_lift=round(marks_lost_to_neg * 0.6, 2),
            priority_score=round(marks_lost_to_neg * 2.0, 2),
            kind="guessing_hygiene",
            headline=f"You lost {marks_lost_to_neg:.1f} marks to negative marking",
            detail=(
                "When confidence is low (< 50 %), skip rather than guess. "
                "Halving your negative marks is often worth more than adding 2 attempts."
            ),
        ))

    # High-weight topic nudge — if weak student hasn't hit one of the
    # exam's high-weight topics in the top-3 already, surface it explicitly.
    if bucket == "weak" and registry_entry:
        already = {r.topic_code for r in recs if r.topic_code}
        for hw in registry_entry.get("high_weight_topics", []):
            tc = hw.get("topic_code")
            if not tc or tc in already:
                continue
            ms = hw.get("marks_share", 0)
            if ms < 4:
                continue
            rank += 1
            recs.append(Recommendation(
                rank=rank,
                topic=hw.get("topic") or tc,
                topic_code=tc,
                subject=hw.get("subject") or hw.get("section", "GENERAL"),
                effort_tier=hw.get("effort_tier") or "B",
                marks_lost=0.0,  # we don't know; it's a nudge
                estimated_marks_lift=round(ms * 0.5, 2),
                priority_score=round(ms * _TIER_MULTIPLIERS.get(hw.get("effort_tier", "B"), 1.0), 2),
                kind="high_weight_nudge",
                headline=f"{hw.get('topic')} fetches {ms:.0f} marks in this paper",
                detail=(
                    (hw.get("rationale") or "")
                    + " Mastering this one topic closes a large % of the gap to a passing score."
                ).strip(),
                study_shortcut=hw.get("study_shortcut"),
                practice_launch={"subject": hw.get("subject"), "topic_code": tc},
            ))
            break  # only one nudge, else the list gets cluttered

    # Final order: by priority_score desc, re-rank 1..N
    recs.sort(key=lambda r: -r.priority_score)
    for i, r in enumerate(recs, start=1):
        r.rank = i
    return recs
