"""Generate a Q-level blueprint for one mock test.

Given an exam's ``ExamPattern`` (from ``seed_exam_structure.py``) and its
topic-frequency table (from ``pyq_ingest.topic_frequency``), this module
produces a deterministic blueprint listing, for each question slot in the
mock: which subject it belongs to, which topic the generator should write
it about, and what difficulty band (EASY / MEDIUM / HARD) it should sit in.

The blueprint exists so that mock generation is *reproducible* and *auditable*:
two different sessions asked to generate Mock #3 for SBI PO Prelims will
produce a mock with the same topic mix, not two randomly-different ones.
Generation quality (the actual question content) is then a separate concern
from distribution fidelity.

Design
------

For each section of the exam pattern:
  * Look up the target subject's topic distribution in the frequency table.
  * Discard UNCLASSIFIED (we don't want the mock to be dominated by
    unlabelled content).
  * Discard any topic tagged ``staleness_risk >= 2`` — mocks must stay
    static (see ``feedback_no_current_affairs_in_mocks.md``).
  * Normalize remaining shares to sum to 100 % within the subject.
  * Allocate section's ``question_count`` slots proportionally via the
    *largest-remainder* method (a.k.a. Hare–Niemeyer) so allocations are
    integer and fair.
  * Within each topic, split the slot count into difficulty bands using the
    topic's observed difficulty mix from the frequency table, applying
    largest-remainder again.

The blueprint is stable: re-running produces byte-identical JSON for the
same inputs.

CLI
---

From ``backend/`` run::

    python -m scripts.mock_gen.blueprint \\
        --frequency-dir /tmp/topic_frequency \\
        --exam sbi-po --stage prelims \\
        --mock-index 1 \\
        --out backend/seeds/mocks/banks/sbi-po/prelims/mock-01.blueprint.json
"""
from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

log = logging.getLogger("mock_blueprint")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# --------------------------------------------------------------------------- #
# Exam patterns — mirrored from ``seed_exam_structure.py`` so this module can
# run standalone (no DB dependency). If you edit the DB seed blueprint,
# reflect the change here.
# --------------------------------------------------------------------------- #

EXAM_PATTERNS: Dict[Tuple[str, str], dict] = {
    ("sbi-po", "prelims"): {
        "total_duration_minutes": 60,
        "total_questions": 100,
        "has_sectional_timing": True,
        "negative_mark": 0.25,
        "sections": [
            {"name": "English Language", "subject": "ENGLISH", "qcount": 30, "duration": 20},
            {"name": "Quantitative Aptitude", "subject": "QUANT", "qcount": 35, "duration": 20},
            {"name": "Reasoning Ability", "subject": "REASONING", "qcount": 35, "duration": 20},
        ],
    },
    ("sbi-po", "mains"): {
        "total_duration_minutes": 180,
        "total_questions": 155,
        "has_sectional_timing": True,
        "negative_mark": 0.25,
        "sections": [
            {"name": "Reasoning & Computer Aptitude", "subject": "REASONING", "qcount": 45, "duration": 60},
            {"name": "Data Analysis & Interpretation", "subject": "DATA_INTERPRETATION", "qcount": 35, "duration": 45},
            {"name": "General / Economy / Banking Awareness", "subject": "GENERAL_AWARENESS", "qcount": 40, "duration": 35},
            {"name": "English Language", "subject": "ENGLISH", "qcount": 35, "duration": 40},
        ],
    },
    ("ibps-po", "prelims"): {
        "total_duration_minutes": 60,
        "total_questions": 100,
        "has_sectional_timing": True,
        "negative_mark": 0.25,
        "sections": [
            {"name": "English Language", "subject": "ENGLISH", "qcount": 30, "duration": 20},
            {"name": "Quantitative Aptitude", "subject": "QUANT", "qcount": 35, "duration": 20},
            {"name": "Reasoning Ability", "subject": "REASONING", "qcount": 35, "duration": 20},
        ],
    },
    ("ibps-po", "mains"): {
        "total_duration_minutes": 180,
        "total_questions": 155,
        "has_sectional_timing": True,
        "negative_mark": 0.25,
        "sections": [
            {"name": "Reasoning & Computer Aptitude", "subject": "REASONING", "qcount": 45, "duration": 60},
            {"name": "English Language", "subject": "ENGLISH", "qcount": 35, "duration": 40},
            {"name": "Data Analysis & Interpretation", "subject": "DATA_INTERPRETATION", "qcount": 35, "duration": 45},
            {"name": "General / Economy / Banking Awareness", "subject": "GENERAL_AWARENESS", "qcount": 40, "duration": 35},
        ],
    },
    ("cgl", "tier-1"): {
        "total_duration_minutes": 60,
        "total_questions": 100,
        "has_sectional_timing": False,
        "negative_mark": 0.5,
        "sections": [
            {"name": "General Intelligence & Reasoning", "subject": "REASONING", "qcount": 25, "marks_per_q": 2.0},
            {"name": "General Awareness", "subject": "GENERAL_AWARENESS", "qcount": 25, "marks_per_q": 2.0},
            {"name": "Quantitative Aptitude", "subject": "QUANT", "qcount": 25, "marks_per_q": 2.0},
            {"name": "English Comprehension", "subject": "ENGLISH", "qcount": 25, "marks_per_q": 2.0},
        ],
    },
    ("chsl", "tier-1"): {
        "total_duration_minutes": 60,
        "total_questions": 100,
        "has_sectional_timing": False,
        "negative_mark": 0.5,
        "sections": [
            {"name": "English Language", "subject": "ENGLISH", "qcount": 25, "marks_per_q": 2.0},
            {"name": "General Awareness", "subject": "GENERAL_AWARENESS", "qcount": 25, "marks_per_q": 2.0},
            {"name": "Quantitative Aptitude", "subject": "QUANT", "qcount": 25, "marks_per_q": 2.0},
            {"name": "General Intelligence", "subject": "REASONING", "qcount": 25, "marks_per_q": 2.0},
        ],
    },
    ("ntpc", "cbt-1"): {
        "total_duration_minutes": 90,
        "total_questions": 100,
        "has_sectional_timing": False,
        "negative_mark": 0.3333,
        "sections": [
            {"name": "General Awareness", "subject": "GENERAL_AWARENESS", "qcount": 40},
            {"name": "Mathematics", "subject": "QUANT", "qcount": 30},
            {"name": "General Intelligence & Reasoning", "subject": "REASONING", "qcount": 30},
        ],
    },
    ("ntpc", "cbt-2"): {
        "total_duration_minutes": 90,
        "total_questions": 120,
        "has_sectional_timing": False,
        "negative_mark": 0.3333,
        "sections": [
            {"name": "General Awareness", "subject": "GENERAL_AWARENESS", "qcount": 50},
            {"name": "Mathematics", "subject": "QUANT", "qcount": 35},
            {"name": "General Intelligence & Reasoning", "subject": "REASONING", "qcount": 35},
        ],
    },
}


# Fallback topic distribution for subjects where the frequency table has
# insufficient signal (e.g. when PYQ papers have too many UNCLASSIFIED Qs).
# Drawn from published Testbook/Oliveboard analyses of SBI/IBPS/SSC papers —
# treat as sane defaults, not ground truth.
FALLBACK_TOPIC_MIX: Dict[str, Dict[str, float]] = {
    "ENGLISH": {
        "reading_comprehension": 0.30,
        "cloze_test": 0.15,
        "sentence_improvement": 0.10,
        "para_jumbles": 0.10,
        "synonym_antonym": 0.10,
        "spotting_error": 0.10,
        "one_word_substitution": 0.05,
        "idioms_phrases": 0.05,
        "fill_preposition": 0.05,
    },
    "QUANT": {
        "simplification": 0.12,
        "percentage": 0.12,
        "profit_loss_discount": 0.10,
        "ratio_proportion": 0.10,
        "time_speed_distance": 0.08,
        "time_and_work": 0.07,
        "mensuration_2d": 0.08,
        "mensuration_3d": 0.05,
        "average": 0.07,
        "number_series": 0.07,
        "simple_compound_interest": 0.06,
        "mixtures_alligation": 0.04,
        "probability": 0.02,
        "permutation_combination": 0.02,
    },
    "REASONING": {
        "seating_arrangement_linear": 0.15,
        "seating_arrangement_circular": 0.15,
        "puzzle_floor": 0.10,
        "puzzle_month_day": 0.10,
        "syllogism": 0.12,
        "blood_relations": 0.08,
        "direction_sense": 0.08,
        "coding_decoding": 0.08,
        "inequality": 0.08,
        "data_sufficiency": 0.06,
    },
    "GENERAL_AWARENESS": {
        "polity_constitution": 0.18,
        "modern_history": 0.12,
        "medieval_history": 0.08,
        "ancient_history": 0.08,
        "geography_india": 0.12,
        "geography_world": 0.05,
        "economy": 0.08,
        "science_physics": 0.06,
        "science_chemistry": 0.06,
        "science_biology": 0.08,
        "culture": 0.04,
        "sports": 0.03,
        "awards_books": 0.02,
    },
    "DATA_INTERPRETATION": {
        "bar_chart": 0.22,
        "line_chart": 0.18,
        "pie_chart": 0.18,
        "table": 0.22,
        "caselet": 0.12,
        "mixed_graph": 0.08,
    },
    "COMPUTER": {
        "fundamentals": 0.50,
        "networking": 0.30,
        "applications": 0.15,
        "shortcuts": 0.05,
    },
}


# --------------------------------------------------------------------------- #
# Core allocation
# --------------------------------------------------------------------------- #

def _largest_remainder(shares: Dict[str, float], total: int) -> Dict[str, int]:
    """Apportion ``total`` integer slots across keys according to their
    fractional ``shares`` using the largest-remainder method.

    The shares are renormalised to sum to 1.0 inside this function so callers
    don't need to worry about that.
    """
    if total <= 0 or not shares:
        return {k: 0 for k in shares}
    s = sum(shares.values()) or 1.0
    raw = {k: v / s * total for k, v in shares.items()}
    floors = {k: int(math.floor(v)) for k, v in raw.items()}
    deficit = total - sum(floors.values())
    if deficit > 0:
        # Sort keys by fractional remainder, descending; allocate leftover slots.
        order = sorted(raw.items(), key=lambda kv: kv[1] - math.floor(kv[1]), reverse=True)
        for key, _ in order[:deficit]:
            floors[key] += 1
    return floors


def _load_topic_frequency(freq_dir: Path, exam_slug: str, stage_slug: str) -> Optional[dict]:
    """Load the topic-frequency JSON that matches the exam and stage, or
    None when we have no PYQ signal for that bucket."""
    # topic_frequency.py writes filenames like "sbi-po__prelims.json"
    fname = f"{exam_slug}__{stage_slug}.json"
    path = freq_dir / fname
    if not path.exists():
        log.warning("no frequency file for %s / %s at %s — falling back to default mix", exam_slug, stage_slug, path)
        return None
    return json.loads(path.read_text())


def _topic_mix_for_subject(freq_doc: Optional[dict], subject: str) -> Dict[str, float]:
    """Return the topic → share mapping for ``subject`` in this exam.

    Strategy:
      * If PYQ-derived data has < 4 distinct topics, rely entirely on the
        static default mix (``FALLBACK_TOPIC_MIX``) — a narrow PYQ signal
        produces lopsided mocks (e.g. "100 % direction_sense reasoning").
      * If PYQ data has 4+ topics, **blend** it 65 / 35 with the default mix.
        PYQ distribution dominates (paper-setters really do over-weight
        certain topics per exam), but the default fills gaps for topics
        the keyword classifier missed entirely.
      * Normalisation across the union of both sources ensures topics that
        only appear in one side still carry their share.
    """
    default = dict(FALLBACK_TOPIC_MIX.get(subject, {"UNCLASSIFIED": 1.0}))
    if freq_doc is None:
        return default
    subj = freq_doc.get("by_subject", {}).get(subject)
    if not subj:
        return default
    pyq_counts = {t: float(v["count"]) for t, v in subj.get("topics", {}).items()
                  if t != "UNCLASSIFIED"}
    if len(pyq_counts) < 4:
        return default
    pyq_total = sum(pyq_counts.values()) or 1.0
    pyq_shares = {t: n / pyq_total for t, n in pyq_counts.items()}
    all_topics = set(pyq_shares) | set(default)
    blended: Dict[str, float] = {}
    for t in all_topics:
        blended[t] = 0.65 * pyq_shares.get(t, 0.0) + 0.35 * default.get(t, 0.0)
    # Re-normalise
    total = sum(blended.values()) or 1.0
    return {t: v / total for t, v in blended.items()}


def _difficulty_mix_for_topic(freq_doc: Optional[dict], subject: str, topic: str) -> Dict[str, float]:
    """Return EASY/MEDIUM/HARD shares for this subject+topic (defaults used
    when we have no signal)."""
    default = {"EASY": 0.30, "MEDIUM": 0.50, "HARD": 0.20}
    if freq_doc is None:
        return default
    tdata = freq_doc.get("by_subject", {}).get(subject, {}).get("topics", {}).get(topic, {})
    mix = tdata.get("difficulty_mix") or {}
    if not mix:
        return default
    return {k: float(v) for k, v in mix.items() if v > 0}


# --------------------------------------------------------------------------- #
# Blueprint schema
# --------------------------------------------------------------------------- #

@dataclass
class BlueprintSlot:
    """One question slot in the blueprint."""
    order: int                 # 1-based global position within the mock
    section_order: int
    section_name: str
    subject: str
    topic: str
    topic_code_hint: str       # produced by topic_codes.get_topic_code for the generator
    difficulty: str


@dataclass
class BlueprintSection:
    """One section's breakdown."""
    order: int
    name: str
    subject: str
    question_count: int
    duration_minutes: Optional[int] = None
    marks_per_question: float = 1.0
    topic_distribution: Dict[str, int] = field(default_factory=dict)


@dataclass
class MockBlueprint:
    """The full blueprint for one mock test."""
    exam_slug: str
    stage_slug: str
    mock_index: int
    total_questions: int
    total_duration_minutes: int
    has_sectional_timing: bool
    negative_mark: float
    sections: List[BlueprintSection]
    slots: List[BlueprintSlot]
    notes: Optional[str] = None


# --------------------------------------------------------------------------- #
# Generator
# --------------------------------------------------------------------------- #

def build_blueprint(
    exam_slug: str,
    stage_slug: str,
    mock_index: int,
    freq_dir: Path,
) -> MockBlueprint:
    key = (exam_slug, stage_slug)
    pattern = EXAM_PATTERNS.get(key)
    if pattern is None:
        raise ValueError(f"no exam pattern for {key}")
    freq_doc = _load_topic_frequency(freq_dir, exam_slug, stage_slug)

    # Import here to avoid circular import when this file is used standalone.
    from scripts.pyq_ingest.topic_codes import get_topic_code

    sections_out: List[BlueprintSection] = []
    slots_out: List[BlueprintSlot] = []
    running_order = 0

    for i, sec in enumerate(pattern["sections"], start=1):
        subject = sec["subject"]
        qcount = sec["qcount"]
        topic_shares = _topic_mix_for_subject(freq_doc, subject)
        topic_counts = _largest_remainder(topic_shares, qcount)

        # Drop zero-allocated topics for cleanliness
        topic_counts = {t: n for t, n in topic_counts.items() if n > 0}

        section = BlueprintSection(
            order=i,
            name=sec["name"],
            subject=subject,
            question_count=qcount,
            duration_minutes=sec.get("duration"),
            marks_per_question=sec.get("marks_per_q", 1.0),
            topic_distribution=dict(topic_counts),
        )
        sections_out.append(section)

        # Expand topics → per-question slots with difficulty assignment.
        for topic, n_slots in topic_counts.items():
            diff_shares = _difficulty_mix_for_topic(freq_doc, subject, topic)
            diff_counts = _largest_remainder(diff_shares, n_slots)
            for diff, dn in diff_counts.items():
                for _ in range(dn):
                    running_order += 1
                    slots_out.append(BlueprintSlot(
                        order=running_order,
                        section_order=i,
                        section_name=sec["name"],
                        subject=subject,
                        topic=topic,
                        topic_code_hint=get_topic_code(subject, topic),
                        difficulty=diff,
                    ))

    # Sanity check: total slots == pattern's total Qs
    if len(slots_out) != pattern["total_questions"]:
        log.warning(
            "slot count %d != exam pattern total %d — adjust allocation",
            len(slots_out), pattern["total_questions"],
        )

    return MockBlueprint(
        exam_slug=exam_slug,
        stage_slug=stage_slug,
        mock_index=mock_index,
        total_questions=pattern["total_questions"],
        total_duration_minutes=pattern["total_duration_minutes"],
        has_sectional_timing=pattern["has_sectional_timing"],
        negative_mark=pattern["negative_mark"],
        sections=sections_out,
        slots=slots_out,
        notes=(
            f"Blueprint for {exam_slug}/{stage_slug} Mock {mock_index}. "
            f"Topic distribution derived from PYQ frequency table with "
            f"UNCLASSIFIED + staleness-risk topics excluded."
        ),
    )


def serialise(blueprint: MockBlueprint) -> dict:
    """Turn the dataclass tree into JSON-friendly dicts."""
    return {
        "schema_version": 1,
        "exam_slug": blueprint.exam_slug,
        "stage_slug": blueprint.stage_slug,
        "mock_index": blueprint.mock_index,
        "total_questions": blueprint.total_questions,
        "total_duration_minutes": blueprint.total_duration_minutes,
        "has_sectional_timing": blueprint.has_sectional_timing,
        "negative_mark": blueprint.negative_mark,
        "sections": [asdict(s) for s in blueprint.sections],
        "slots": [asdict(s) for s in blueprint.slots],
        "notes": blueprint.notes,
    }


def main() -> int:
    import sys
    ap = argparse.ArgumentParser()
    ap.add_argument("--frequency-dir", default="/tmp/topic_frequency",
                    help="Directory containing *.json topic-frequency tables")
    ap.add_argument("--exam", required=True)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--mock-index", type=int, default=1)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    bp = build_blueprint(args.exam, args.stage, args.mock_index, Path(args.frequency_dir))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(serialise(bp), indent=2))
    log.info(
        "blueprint written: %s — %d slots across %d sections",
        args.out, len(bp.slots), len(bp.sections),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
