"""Emit a generation brief for the next-priority topic.

Output (stdout, JSON):
    {
      "topic_code", "subject", "topic", "existing_count",
      "existing_stems": ["already-asked stem 1", ...],
      "rules": {... full gate rules ...},
      "staging_path": "/tmp/auto_seed_staging_<topic>.json",
      "expected_schema": "A | B (both accepted by apply)"
    }

Used by Claude-in-session to compose the next 7-Q bundle without
re-reading the topic's bundle file by hand.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .canonical import SUBJECT_FOLDER
from .priority import next_picks

_BACKEND = Path(__file__).resolve().parents[2]
_STATE = _BACKEND / "scripts" / "auto_seed" / "state.json"
_POOL = _BACKEND / "seeds" / "static_gk"


def _existing_stems_for(topic_code: str) -> list[str]:
    stems: list[str] = []
    # Search across all subject folders since topic_code is unique
    for f in _POOL.rglob(f"{topic_code}.json"):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        for q in d.get("questions", []):
            s = q.get("stem") or q.get("text")
            if s:
                stems.append(s)
    return stems


def make_brief(topic_code: str | None = None, exclude_codes: set[str] | None = None) -> dict:
    state = json.loads(_STATE.read_text())
    if topic_code:
        # User specified a topic — find it in state
        for t in state["topics"]:
            if t["topic_code"] == topic_code:
                pick = {
                    "topic_code": topic_code,
                    "subject": t["subject"],
                    "topic": t["topic"],
                    "existing": t["questions"],
                    "high_weight": False,
                }
                break
        else:
            return {"error": f"topic_code {topic_code} not in state"}
    else:
        picks = next_picks(state, n=1, exclude=exclude_codes or set())
        if not picks:
            return {"error": "no candidate topics — pool may be saturated"}
        pick = picks[0]

    existing_stems = _existing_stems_for(pick["topic_code"])
    folder = SUBJECT_FOLDER.get(pick["subject"], "general_knowledge")

    return {
        "topic_code": pick["topic_code"],
        "subject": pick["subject"],
        "topic": pick["topic"],
        "high_weight": pick.get("high_weight", False),
        "existing_count": pick["existing"],
        "target": pick.get("target"),
        "deficit": pick.get("deficit"),
        "priority": pick.get("priority"),
        "bundle_path": f"seeds/static_gk/{folder}/{pick['topic_code']}.json",
        "staging_path": f"/tmp/auto_seed_staging_{pick['topic_code']}.json",
        "existing_stems": existing_stems,
        "rules": {
            "questions_per_file": 7,
            "difficulty_shape_options": ["2-easy/3-medium/2-hard", "2-easy/4-medium/1-hard"],
            "difficulty_per_q_strict_order": "Q1-Q2 easy, Q3-Q5 medium, Q6-Q7 hard",
            "options_per_q": 4,
            "option_keys": "A/B/C/D",
            "parity_max_ratio": "len(correct)/min(len(wrong)) < 1.30 — pad SHORT WRONG options, never the correct one",
            "explanation_required": "yes, ≥30 chars; should justify correct AND why tempting wrong is wrong",
            "subject_must_be_canonical": "one of the 14 canonical strings; new files must match existing canonical",
            "schema": "either A (stem/option_text+is_correct/correct_letter, uppercase difficulty) or B (text/key+text/correct, lowercase difficulty) — apply auto-transcodes B→A",
            "must_not_overlap_existing_stems": "see 'existing_stems' list — generate complementary angles, not paraphrases",
            "no_visible_tier_tags": "no [Clerk tier] / [CGL tier] / [Mains] prefixes in stems",
            "no_absolute_language_in_options": "avoid 'always', 'never', 'all of the above', 'none of the above'",
            "no_post_2020_facts": "static answers only; no current affairs or appointment-based facts",
            "exam_relevance": "must be plausibly set by SSC CGL/CHSL/IBPS/SBI/RRB examiner; pick under-asked angles on high-PYQ topics",
        },
        "exam_relevance_hint": (
            "Prioritise questions that examiners actually set: under-asked angles on "
            "core topics, GI tags, folk arts, niche but PYQ-frequent terminology. Avoid "
            "namesake/trivial stems where the answer is obvious from the question."
        ),
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("topic_code", nargs="?", default=None,
                    help="topic_code to brief (default: next-priority pick)")
    ap.add_argument("--json", action="store_true", help="emit raw JSON only")
    args = ap.parse_args()
    brief = make_brief(args.topic_code)
    if args.json:
        print(json.dumps(brief, indent=2, ensure_ascii=False))
        return 0 if "error" not in brief else 1
    if "error" in brief:
        print(f"error: {brief['error']}")
        return 1
    print(f"NEXT PICK: {brief['topic_code']}")
    print(f"  subject: {brief['subject']}  topic: {brief['topic']}")
    print(f"  existing: {brief['existing_count']}  target: {brief['target']}  "
          f"deficit: {brief['deficit']}  priority: {brief['priority']}")
    print(f"  bundle_path: {brief['bundle_path']}")
    print(f"  staging_path: {brief['staging_path']}")
    print(f"  high_weight: {brief['high_weight']}")
    print(f"  existing stems ({len(brief['existing_stems'])}):")
    for s in brief["existing_stems"][:20]:
        print(f"    - {s[:120]}")
    if len(brief["existing_stems"]) > 20:
        print(f"    ... +{len(brief['existing_stems']) - 20} more")
    print()
    print("Rules:")
    for k, v in brief["rules"].items():
        print(f"  • {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
