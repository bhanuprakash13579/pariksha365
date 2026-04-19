"""Compile ``high_weight_topics.json`` from the per-exam syllabus JSONs.

Reads every ``backend/seeds/_syllabus/*.json`` file and emits a single
consolidated registry at ``backend/seeds/_analysis/high_weight_topics.json``.
The registry is what the mock generator and feedback engine consume.

Each exam's top topics are selected by ranking:
  1. topics with highest ``expected_qs`` × ``marks_per_q`` (marks share)
  2. topics flagged explicitly as HIGH WEIGHT in the source syllabus notes
  3. topics with effort_tier == 'A' whose ``expected_qs`` ≥ 2 (quick wins)

A per-exam ``efficiency_pitch`` string is carried through verbatim so the
UI can render it without reformatting.

Run::

    python -m scripts.mock_gen.build_registry

Output replaces ``seeds/_analysis/high_weight_topics.json`` — the source of
truth for both mock-generation weighting and feedback-engine ranking.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

log = logging.getLogger("build_registry")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


EFFORT_MULTIPLIERS = {"A": 3.0, "B": 1.5, "C": 0.7}


def _marks_per_q(section: dict, pattern: dict) -> float:
    """Return marks-per-question for this section, preferring the section's
    own override over the pattern default."""
    if "marks_per_question" in section:
        return float(section["marks_per_question"])
    # Fallback: section marks / Q count
    qc = section.get("question_count") or 1
    return float(section.get("marks", qc)) / qc


def _build_entry(section: dict, topic: dict, pattern: dict, exam_total_marks: float) -> dict:
    mpq = _marks_per_q(section, pattern)
    expected_qs = int(topic.get("expected_qs") or 0)
    marks_share = expected_qs * mpq
    share_pct = round(100 * marks_share / max(1.0, exam_total_marks), 2)
    tier = topic.get("effort_tier", "B")
    mult = EFFORT_MULTIPLIERS.get(tier, 1.0)
    # Priority: Tier A with high marks_share → weak_student; Tier C → advanced_student
    if tier == "A":
        priority = "weak_student"
    elif tier == "C":
        priority = "advanced_student"
    else:
        priority = "weak_student" if marks_share >= 4 else "balanced"
    return {
        "section": section["name"],
        "subject": section["subject"],
        "topic": topic["topic"],
        "topic_code": topic.get("topic_code"),
        "expected_qs": expected_qs,
        "marks_share": round(marks_share, 2),
        "share_pct": share_pct,
        "effort_tier": tier,
        "priority_score_multiplier": mult,
        "priority": priority,
        "study_shortcut": topic.get("study_shortcut"),
        "notes": topic.get("notes"),
    }


def compile_registry(syllabus_dir: Path, out_path: Path) -> int:
    registry: Dict[str, dict] = {}

    for sf in sorted(syllabus_dir.glob("*__*.json")):
        doc = json.loads(sf.read_text())
        exam_slug = doc["exam_slug"]
        stage_slug = doc["stage_slug"]
        key = f"{exam_slug}__{stage_slug}"

        pattern = doc.get("exam_pattern") or {}
        total_marks = float(
            pattern.get("total_marks")
            or pattern.get("total_marks_objective")
            or 100
        )

        # Build flat list of topic entries across all sections
        entries: List[dict] = []
        for sec in doc.get("sections", []):
            for topic in sec.get("topics", []):
                if not topic.get("topic"):
                    continue
                entries.append(_build_entry(sec, topic, pattern, total_marks))

        # Sort by: tier A first → marks_share desc → share_pct
        def _sort_key(e: dict):
            tier_rank = {"A": 0, "B": 1, "C": 2}.get(e["effort_tier"], 3)
            return (tier_rank, -e["marks_share"], -e["share_pct"])

        entries.sort(key=_sort_key)

        # Top-12 entries form the "high weight" list for the registry;
        # callers can reference the full syllabus JSON for completeness.
        top_entries = entries[:12]

        # Rollup stats
        tier_counts = {"A": 0, "B": 0, "C": 0}
        tier_marks = {"A": 0.0, "B": 0.0, "C": 0.0}
        for e in entries:
            tier_counts[e["effort_tier"]] = tier_counts.get(e["effort_tier"], 0) + 1
            tier_marks[e["effort_tier"]] = tier_marks.get(e["effort_tier"], 0) + e["marks_share"]

        registry[key] = {
            "exam": doc.get("notes", "").split(".")[0] or exam_slug.upper(),
            "exam_slug": exam_slug,
            "stage_slug": stage_slug,
            "total_marks": total_marks,
            "tier_counts": tier_counts,
            "tier_marks_share": {k: round(v, 1) for k, v in tier_marks.items()},
            "tier_marks_share_pct_of_paper": {
                k: round(100 * v / max(1.0, total_marks), 1) for k, v in tier_marks.items()
            },
            "efficiency_pitch": doc.get("efficiency_pitch"),
            "high_weight_topics": top_entries,
            "full_topic_count": len(entries),
        }

    out = {
        "schema_version": 3,
        "generated_at_note": "Regenerate by running scripts.mock_gen.build_registry. Do not edit by hand.",
        "effort_tier_legend": {
            "A": "Quick-wins: <2 study hours/mark. Finite facts, pattern drills, short lists.",
            "B": "Standard: 2-5 study hours/mark. Concept + drill.",
            "C": "Heavy: >5 study hours/mark. Vast vocab, abstract reasoning.",
        },
        "effort_multipliers": EFFORT_MULTIPLIERS,
        "how_to_consume": {
            "mock_generator": "Use marks_share to drive question allocation. Use effort_tier only as metadata for feedback — don't bias generation.",
            "feedback_engine": "Rank recommendations by (marks_lost × priority_score_multiplier). Surface top-3 with study_shortcut verbatim.",
            "admin_ui": "Separate panels: marks-share heatmap + effort-ROI tier map.",
        },
        "registry": registry,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    log.info("wrote %s", out_path)
    log.info("exams compiled: %d", len(registry))
    for k, v in registry.items():
        log.info(
            "  %-22s  A=%d B=%d C=%d  pitch=%s",
            k,
            v["tier_counts"].get("A", 0),
            v["tier_counts"].get("B", 0),
            v["tier_counts"].get("C", 0),
            "yes" if v["efficiency_pitch"] else "no",
        )
    return 0


def main() -> int:
    base = Path(__file__).resolve().parents[2] / "seeds"
    return compile_registry(base / "_syllabus", base / "_analysis" / "high_weight_topics.json")


if __name__ == "__main__":
    sys.exit(main())
