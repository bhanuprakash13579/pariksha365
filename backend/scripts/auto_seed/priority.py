"""Next-gap picker.

Score each topic_code by:
  priority = (deficit) * subject_weight * coverage_factor * high_weight_bonus

deficit = max(0, target - existing)
subject_weight = fraction of 50k allocated to that subject
coverage_factor = 1.0 normally; 0.5 if existing >= 200 (saturation); 1.3 if existing < 7 (under-covered)
high_weight_bonus = 1.4 if topic_code is in high_weight_topics.json, else 1.0

Subject weights aligned with cross-exam marks share. QRE block roughly 40%,
Sci/Static-GK 60% — per the user's split target.
"""
from __future__ import annotations

import json
from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[2]
_STATE = _BACKEND / "scripts" / "auto_seed" / "state.json"
_HIGH_WEIGHT = _BACKEND / "seeds" / "_analysis" / "high_weight_topics.json"

SUBJECT_WEIGHT_TARGETS: dict[str, int] = {
    # QRE block (~20k total per user spec)
    "Quantitative Aptitude": 6000,
    "Reasoning": 5000,
    "English": 5000,
    "Vocabulary": 4000,
    # Static GK + Science (~30k total)
    "Polity": 4500,
    "History": 4500,
    "Geography": 4000,
    "Biology": 3000,
    "Chemistry": 3000,
    "Physics": 3000,
    "Economics": 3000,
    "General Knowledge": 5000,
    "Environment": 2000,
    "Computer Science": 0,  # legacy folder; no new growth
}

_PER_TOPIC_CAP = 200  # don't let any one topic exceed this much


def _high_weight_codes() -> set[str]:
    if not _HIGH_WEIGHT.exists():
        return set()
    try:
        doc = json.loads(_HIGH_WEIGHT.read_text())
    except Exception:
        return set()
    out: set[str] = set()
    for entry in (doc.get("registry") or {}).values():
        for hw in entry.get("high_weight_topics") or []:
            tc = hw.get("topic_code")
            if tc:
                out.add(tc)
    return out


def score_topics(state: dict) -> list[dict]:
    hw = _high_weight_codes()
    by_subj_count = {s: 0 for s in SUBJECT_WEIGHT_TARGETS}
    for t in state.get("topics", []):
        if t["subject"] in by_subj_count:
            by_subj_count[t["subject"]] += 1
    # Compute per-topic share for each subject
    per_subj_target_per_topic = {
        s: (SUBJECT_WEIGHT_TARGETS[s] / max(1, by_subj_count[s]))
        for s in SUBJECT_WEIGHT_TARGETS
    }
    rows: list[dict] = []
    for t in state.get("topics", []):
        subj = t["subject"]
        if subj not in SUBJECT_WEIGHT_TARGETS:
            continue
        if SUBJECT_WEIGHT_TARGETS[subj] == 0:
            continue
        base_target = per_subj_target_per_topic[subj]
        # Cap per-topic so single topics don't dominate
        target = min(_PER_TOPIC_CAP, base_target * (1.4 if t["topic_code"] in hw else 1.0))
        existing = t["questions"]
        deficit = max(0, target - existing)
        if existing >= 200:
            coverage_factor = 0.4  # saturated; only grow if priority overwhelming
        elif existing < 7:
            coverage_factor = 1.3  # under-covered
        else:
            coverage_factor = 1.0
        hw_bonus = 1.4 if t["topic_code"] in hw else 1.0
        priority = deficit * coverage_factor * hw_bonus
        rows.append({
            "topic_code": t["topic_code"],
            "subject": subj,
            "topic": t["topic"],
            "existing": existing,
            "target": round(target),
            "deficit": round(deficit, 1),
            "priority": round(priority, 1),
            "high_weight": t["topic_code"] in hw,
            "schema_versions": t.get("schema_versions", []),
            "needs_transcode": t.get("needs_transcode", False),
            "needs_subject_canon": t.get("needs_subject_canon", False),
            "parity_fails": t.get("parity_fails", 0),
        })
    rows.sort(key=lambda r: -r["priority"])
    return rows


def next_picks(state: dict, n: int = 1, exclude: set[str] | None = None) -> list[dict]:
    exclude = exclude or set()
    rows = score_topics(state)
    return [r for r in rows if r["topic_code"] not in exclude][:n]


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", type=int, default=10)
    ap.add_argument("--subject", default=None, help="Filter to one subject")
    args = ap.parse_args()
    state = json.loads(_STATE.read_text())
    rows = score_topics(state)
    if args.subject:
        rows = [r for r in rows if r["subject"] == args.subject]
    rows = rows[:args.n]
    print(f"Top {len(rows)} priority picks:")
    print(f"  {'topic_code':<45} {'subject':<22} {'existing':>8} {'target':>7} {'priority':>10}")
    for r in rows:
        hw = "★" if r["high_weight"] else " "
        print(f"  {hw}{r['topic_code']:<44} {r['subject']:<22} "
              f"{r['existing']:>8} {r['target']:>7} {r['priority']:>10.1f}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
