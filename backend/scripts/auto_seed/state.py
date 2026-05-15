"""Scan the on-disk seed pool and produce a current-state snapshot.

The existing static_gk_planner.py only knows about 182 topic_codes from
the (stale) existing_quiz_signatures.json. The real pool has 1284+. This
module rebuilds state from what's actually on disk so the autonomous
driver picks the right next gap.

Output: scripts/auto_seed/state.json
{
  "scanned_at": "2026-05-15T...",
  "total_questions": N,
  "by_subject": {subj: {"codes": int, "questions": int}},
  "topics": [
    {"topic_code", "subject", "topic", "questions", "schema",
     "path", "needs_transcode": bool, "needs_subject_canon": bool,
     "parity_fails": int, "difficulty_distribution": [n_easy,n_med,n_hard]}
  ]
}
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import canon_subject, subject_for_code, to_schema_a

_BACKEND = Path(__file__).resolve().parents[2]
_POOL = _BACKEND / "seeds" / "static_gk"
_OUT = _BACKEND / "scripts" / "auto_seed" / "state.json"


def _detect_schema(q: dict) -> str:
    if "stem" in q and ("correct_letter" in q or any(
        "is_correct" in (o or {}) for o in q.get("options", []))):
        return "A"
    if "text" in q and ("correct" in q or any(
        "key" in (o or {}) for o in q.get("options", []))):
        return "B"
    return "?"


def _difficulty_bucket(d: str | None) -> str:
    if not d:
        return "?"
    s = d.upper()
    if "EASY" in s or s == "A": return "easy"
    if "MED" in s or s == "B": return "medium"
    if "HARD" in s or s == "C": return "hard"
    return "?"


def _option_len(o: Any) -> int:
    if isinstance(o, dict):
        return len(o.get("option_text") or o.get("text") or "")
    return 0


def _parity_check(q: dict) -> bool:
    """Return True if option-length parity passes (ratio < 1.30)."""
    opts = q.get("options") or []
    lens = [(o, _option_len(o)) for o in opts]
    if not lens or min(l for _, l in lens) == 0:
        return False
    # find correct option
    correct_idx = -1
    if "correct_letter" in q:
        letters = ("A", "B", "C", "D", "E")
        try:
            correct_idx = letters.index(q["correct_letter"].upper())
        except (ValueError, AttributeError):
            pass
    elif "correct" in q:
        letters = ("A", "B", "C", "D", "E")
        try:
            correct_idx = letters.index(q["correct"].upper())
        except (ValueError, AttributeError):
            pass
    else:
        for i, (o, _) in enumerate(lens):
            if isinstance(o, dict) and o.get("is_correct"):
                correct_idx = i
                break
    if correct_idx < 0 or correct_idx >= len(lens):
        return False
    clen = lens[correct_idx][1]
    wmin = min(l for i, (_, l) in enumerate(lens) if i != correct_idx)
    if wmin == 0:
        return False
    return (clen / wmin) < 1.30


def scan_pool() -> dict:
    topics: dict[str, dict] = {}
    by_subj: dict[str, dict] = {}
    total_q = 0
    parse_errors: list[str] = []

    for f in sorted(_POOL.rglob("*.json")):
        if f.name.startswith("_"):
            continue
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            parse_errors.append(f"{f.relative_to(_BACKEND)}: {e}")
            continue
        qs = d.get("questions") or []
        if not qs:
            continue
        code = d.get("topic_code") or "MISSING"
        raw_subj = d.get("subject")
        canon = canon_subject(raw_subj) or subject_for_code(code) or "MISSING"
        schema = _detect_schema(qs[0])
        # Per-file aggregates
        diff_counts = {"easy": 0, "medium": 0, "hard": 0, "?": 0}
        parity_fails = 0
        for q in qs:
            diff_counts[_difficulty_bucket(q.get("difficulty"))] += 1
            if not _parity_check(q):
                parity_fails += 1
        entry = topics.setdefault(code, {
            "topic_code": code,
            "subject": canon,
            "topic": d.get("topic"),
            "questions": 0,
            "schema_versions": set(),
            "paths": [],
            "needs_transcode": False,
            "needs_subject_canon": False,
            "parity_fails": 0,
            "diff_easy": 0, "diff_medium": 0, "diff_hard": 0, "diff_unknown": 0,
        })
        entry["questions"] += len(qs)
        entry["schema_versions"].add(schema)
        entry["paths"].append(str(f.relative_to(_BACKEND)))
        if schema == "B":
            entry["needs_transcode"] = True
        if raw_subj != canon:
            entry["needs_subject_canon"] = True
        entry["parity_fails"] += parity_fails
        entry["diff_easy"] += diff_counts["easy"]
        entry["diff_medium"] += diff_counts["medium"]
        entry["diff_hard"] += diff_counts["hard"]
        entry["diff_unknown"] += diff_counts["?"]
        total_q += len(qs)
        s = by_subj.setdefault(canon, {"codes": set(), "questions": 0})
        s["codes"].add(code)
        s["questions"] += len(qs)

    # finalise
    for t in topics.values():
        t["schema_versions"] = sorted(t["schema_versions"])
    by_subj_out = {
        s: {"codes": len(v["codes"]), "questions": v["questions"]}
        for s, v in sorted(by_subj.items(), key=lambda kv: -kv[1]["questions"])
    }
    return {
        "scanned_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "total_questions": total_q,
        "total_topics": len(topics),
        "by_subject": by_subj_out,
        "topics": sorted(topics.values(), key=lambda t: (t["subject"], t["topic_code"])),
        "parse_errors": parse_errors,
    }


def main() -> int:
    snap = scan_pool()
    _OUT.write_text(json.dumps(snap, indent=2, ensure_ascii=False))
    print(f"state written: {_OUT.relative_to(_BACKEND)}")
    print(f"  total questions: {snap['total_questions']}")
    print(f"  total distinct topics: {snap['total_topics']}")
    print(f"  parse errors: {len(snap['parse_errors'])}")
    for pe in snap["parse_errors"][:5]:
        print(f"    {pe}")
    print()
    print("  per-subject:")
    for s, v in snap["by_subject"].items():
        print(f"    {v['questions']:5d}q  {v['codes']:4d}codes  {s}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
