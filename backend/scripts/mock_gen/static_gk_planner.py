"""Produce a per-topic Q-count plan for the 50 k static-GK pool.

Inputs
------
* ``seeds/_dedup/existing_quiz_signatures.json`` — 183 rows of the user's
  existing ``(subject, topic_code, topic, existing_q_count)`` taxonomy. We
  honour this naming — new Qs reuse these topic_codes rather than forking.
* Total target: **50,000 Qs** (can be overridden with ``--target``).

Output
------
``seeds/static_gk/_plan.json`` — a flat list of planner rows, each with:

    {"subject": "Polity", "topic": "Fundamental Rights",
     "topic_code": "POL_FR", "existing": 12, "target": 350,
     "to_generate": 338, "priority_rank": 4, ...}

Weighting rules
---------------

Not every topic gets an equal share. Static-GK for competitive exams is
heavily skewed — Polity/History/Geography need thousands each; niche topics
like ``GEO_IND_TRANSPORT`` need fewer. The planner weights by:

* **Subject weight** — rough marks-share of the subject across the exams
  we support (Polity ≈ 18 %, History ≈ 20 %, Geography ≈ 15 %, General
  Science ≈ 20 %, Economy ≈ 8 %, Static GK ≈ 15 %, etc.).
* **Existing coverage** — topics already over-represented (>150 existing
  Qs) get a lower multiplier so we balance rather than pile on.
* **Priority rank** — topics flagged as high-weight in the 10-exam
  registry get a 1.3× multiplier so the pool has deeper coverage where
  students spend most time.

The planner is deterministic — re-running with the same inputs produces
byte-identical output, making review workflows easy.
"""
from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional

log = logging.getLogger("static_gk_planner")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


# --------------------------------------------------------------------------- #
# Subject-level weights (sum ~1.0). Derived from cross-exam marks-share
# analysis of the 10 exam syllabi in backend/seeds/_syllabus/.
# --------------------------------------------------------------------------- #

SUBJECT_WEIGHTS: Dict[str, float] = {
    "Polity": 0.18,
    "History": 0.18,
    "Geography": 0.15,
    "Biology": 0.08,
    "Physics": 0.06,
    "Chemistry": 0.06,
    "Economics": 0.09,
    "General Knowledge": 0.12,
    "Science & Technology": 0.04,
    "Env & Ecology": 0.03,
    "Current Affairs": 0.00,   # explicitly zero — pool is static-only
    # Any subjects introduced later get DEFAULT weight
}
DEFAULT_SUBJECT_WEIGHT = 0.05


# Topic_codes flagged as high-weight across any of the 10 exam registries.
# Populated from backend/seeds/_analysis/high_weight_topics.json at runtime.

# --------------------------------------------------------------------------- #

@dataclass
class PlanRow:
    subject: str
    topic: str
    topic_code: str
    existing: int
    target: int
    to_generate: int
    priority_rank: int
    priority: str           # "high" | "standard" | "low"
    notes: Optional[str] = None


def _load_existing_taxonomy(dedup_path: Path) -> List[dict]:
    doc = json.loads(dedup_path.read_text())
    rows = doc.get("existing_taxonomy") or []
    # Sanity: every row has subject, topic_code, topic, existing_q_count
    cleaned = []
    for r in rows:
        if not r.get("topic_code"):
            continue
        cleaned.append({
            "subject": r.get("subject") or "General Knowledge",
            "topic_code": r["topic_code"],
            "topic": r.get("topic") or r["topic_code"],
            "existing": int(r.get("existing_q_count") or 0),
        })
    return cleaned


def _load_high_weight_codes(registry_path: Path) -> set[str]:
    """Return the union of every topic_code flagged as high-weight in any of
    the 10 exam registries. These get priority boost in the plan."""
    if not registry_path.exists():
        log.warning("registry missing at %s — no priority boosts applied", registry_path)
        return set()
    doc = json.loads(registry_path.read_text())
    out: set[str] = set()
    for _, entry in doc.get("registry", {}).items():
        for hw in entry.get("high_weight_topics", []):
            tc = hw.get("topic_code")
            if tc:
                out.add(tc)
    return out


def build_plan(dedup_path: Path, registry_path: Path, total_target: int) -> List[PlanRow]:
    taxonomy = _load_existing_taxonomy(dedup_path)
    high_weight = _load_high_weight_codes(registry_path)
    log.info("taxonomy rows: %d, high-weight topic_codes: %d", len(taxonomy), len(high_weight))

    # Group taxonomy by subject
    by_subject: Dict[str, List[dict]] = defaultdict(list)
    for r in taxonomy:
        by_subject[r["subject"]].append(r)

    # Compute per-subject target count from SUBJECT_WEIGHTS
    subject_targets: Dict[str, int] = {}
    total_weight = 0.0
    for subj in by_subject:
        w = SUBJECT_WEIGHTS.get(subj, DEFAULT_SUBJECT_WEIGHT)
        subject_targets[subj] = int(round(total_target * w))
        total_weight += w
    # Normalise if sum drifted from 1.0
    if total_weight > 0 and abs(total_weight - 1.0) > 0.02:
        scale = total_target / sum(subject_targets.values())
        subject_targets = {s: int(round(n * scale)) for s, n in subject_targets.items()}
    log.info("per-subject targets: %s", subject_targets)

    # Within each subject, distribute across topics. Base share = uniform,
    # boosted for high-weight and existing-coverage attenuation.
    rows: List[PlanRow] = []
    for subj, topics in by_subject.items():
        subj_target = subject_targets.get(subj, 0)
        if not subj_target or not topics:
            continue
        # Compute weight per topic
        weights: List[float] = []
        for t in topics:
            w = 1.0
            if t["topic_code"] in high_weight:
                w *= 1.4
            # Dampen topics that already have strong existing coverage
            if t["existing"] >= 150:
                w *= 0.6
            elif t["existing"] >= 80:
                w *= 0.8
            weights.append(w)
        total_w = sum(weights) or 1.0
        shares = [subj_target * (w / total_w) for w in weights]
        # Largest-remainder apportionment so integers sum to subj_target
        floors = [int(math.floor(s)) for s in shares]
        remainder = subj_target - sum(floors)
        order = sorted(range(len(shares)), key=lambda i: shares[i] - math.floor(shares[i]), reverse=True)
        for idx in order[:remainder]:
            floors[idx] += 1
        for t, target in zip(topics, floors):
            is_hw = t["topic_code"] in high_weight
            to_gen = max(0, target - t["existing"])
            rows.append(PlanRow(
                subject=t["subject"],
                topic=t["topic"],
                topic_code=t["topic_code"],
                existing=t["existing"],
                target=target,
                to_generate=to_gen,
                priority_rank=(0 if is_hw else 1),
                priority="high" if is_hw else "standard",
                notes=(
                    "HIGH WEIGHT in cross-exam registry; "
                    "prioritise generation batches here."
                ) if is_hw else None,
            ))

    rows.sort(key=lambda r: (r.priority_rank, -r.to_generate, r.subject, r.topic_code))
    return rows


def summarise(rows: List[PlanRow]) -> dict:
    by_subj: Dict[str, dict] = defaultdict(lambda: {"topics": 0, "target": 0, "existing": 0, "to_generate": 0})
    total_target = total_existing = total_to_gen = 0
    for r in rows:
        s = by_subj[r.subject]
        s["topics"] += 1
        s["target"] += r.target
        s["existing"] += r.existing
        s["to_generate"] += r.to_generate
        total_target += r.target
        total_existing += r.existing
        total_to_gen += r.to_generate
    return {
        "total_topics": len(rows),
        "total_target": total_target,
        "total_existing": total_existing,
        "total_to_generate": total_to_gen,
        "by_subject": dict(by_subj),
    }


def main() -> int:
    backend = Path(__file__).resolve().parents[2]
    ap = argparse.ArgumentParser()
    ap.add_argument("--target", type=int, default=50000, help="Total Qs to reach (default 50000)")
    ap.add_argument("--dedup", default=str(backend / "seeds" / "_dedup" / "existing_quiz_signatures.json"))
    ap.add_argument("--registry", default=str(backend / "seeds" / "_analysis" / "high_weight_topics.json"))
    ap.add_argument("--out", default=str(backend / "seeds" / "static_gk" / "_plan.json"))
    args = ap.parse_args()

    dedup = Path(args.dedup).resolve()
    if not dedup.exists():
        log.error("dedup file missing at %s — run sync_dedup_index first", dedup)
        return 2

    rows = build_plan(dedup, Path(args.registry).resolve(), args.target)
    summary = summarise(rows)

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({
        "schema_version": 1,
        "target_total": args.target,
        "summary": summary,
        "rows": [asdict(r) for r in rows],
    }, indent=2, ensure_ascii=False))
    log.info("plan written: %s", out_path)
    log.info("total: %d topics, target %d Qs (existing %d, to-generate %d)",
             summary["total_topics"], summary["total_target"],
             summary["total_existing"], summary["total_to_generate"])
    log.info("per-subject summary:")
    for subj, s in sorted(summary["by_subject"].items(), key=lambda kv: -kv[1]["target"]):
        log.info("  %-22s topics=%d  target=%d  existing=%d  to-generate=%d",
                 subj, s["topics"], s["target"], s["existing"], s["to_generate"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
