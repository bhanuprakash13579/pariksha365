"""Append generated static-GK questions to the on-disk seed pool with full
dedup validation.

Workflow expected
-----------------

1. The generator (Claude-in-chat, across many sessions) assembles a batch
   of new questions as a Python dict matching :class:`StaticGKBatch`.
2. The generator calls ``apply_batch(batch)`` which:
     a. Loads the existing signatures (``seeds/_dedup/existing_quiz_signatures.json``)
        and the per-topic seed file already on disk
     b. Computes each new Q's normalised-stem signature and rejects
        duplicates (against DB + against other new Qs in the same batch)
     c. Re-uses ``topic_code``/``topic``/``subject`` from the existing
        taxonomy when the batch omits them — never forks the taxonomy
     d. Writes accepted Qs to ``seeds/static_gk/<subject>/<topic_code>.json``
        in the :class:`SeedStaticGKBundle` schema from ``seed_schema.py``
     e. Updates ``seeds/static_gk/_progress.json`` with the running count
        against the plan
3. The generator prints a summary and moves on.

Why this shape
--------------

* **Single entry point** for all batches: callers don't touch files
  directly, so dedup + schema + progress stay in sync.
* **Idempotent** at the question level: re-running a batch that's already
  been applied is a no-op (signatures deduped).
* **Incremental**: each batch extends the pool without rewriting existing
  files, so one session's output doesn't overwrite another's.
* **Auditable**: every saved Q carries ``answer_source='generated'`` and a
  generator-tag so admins can filter for human-review.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

log = logging.getLogger("static_gk_writer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

_WS = re.compile(r"\s+")
_PUNCT = re.compile(r"[^\w\s]", re.UNICODE)

_BACKEND = Path(__file__).resolve().parents[2]
_SEEDS = _BACKEND / "seeds"
_DEDUP_PATH = _SEEDS / "_dedup" / "existing_quiz_signatures.json"
_PLAN_PATH = _SEEDS / "static_gk" / "_plan.json"
_PROGRESS_PATH = _SEEDS / "static_gk" / "_progress.json"
_POOL_DIR = _SEEDS / "static_gk"


# --------------------------------------------------------------------------- #
# Signature helpers (must match sync_dedup_index.py exactly)
# --------------------------------------------------------------------------- #

def normalise_stem(raw: str, max_len: int = 160) -> str:
    if not raw:
        return ""
    s = raw.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s[:max_len]


def normalise_option(raw: str) -> str:
    if not raw:
        return ""
    s = raw.lower()
    s = _PUNCT.sub(" ", s)
    s = _WS.sub(" ", s).strip()
    return s[:60]


# --------------------------------------------------------------------------- #
# Taxonomy + plan loaders
# --------------------------------------------------------------------------- #

@dataclass
class Taxonomy:
    # topic_code -> {"subject","topic","existing_q_count"}
    by_code: Dict[str, dict] = field(default_factory=dict)
    existing_stem_sigs: set = field(default_factory=set)
    existing_topic_first_sigs: set = field(default_factory=set)


def _load_taxonomy_and_sigs() -> Taxonomy:
    tax = Taxonomy()
    if not _DEDUP_PATH.exists():
        log.warning("%s missing — run sync_dedup_index first. Taxonomy will be empty.", _DEDUP_PATH)
        return tax
    doc = json.loads(_DEDUP_PATH.read_text())
    for r in doc.get("existing_taxonomy", []):
        tc = r.get("topic_code")
        if not tc:
            continue
        tax.by_code[tc] = {
            "subject": r.get("subject"),
            "topic": r.get("topic"),
            "existing_q_count": int(r.get("existing_q_count") or 0),
        }
    tax.existing_stem_sigs = set(doc.get("stem_signatures") or [])
    tax.existing_topic_first_sigs = set(doc.get("topic_first_signatures") or [])
    return tax


def _load_pool_sigs() -> tuple[set, set]:
    """Collect signatures from already-written bundles so batches applied in
    earlier sessions of this codebase dedup correctly."""
    stem: set = set()
    tfsig: set = set()
    if not _POOL_DIR.exists():
        return stem, tfsig
    for bundle_file in _POOL_DIR.rglob("*.json"):
        if bundle_file.name.startswith("_"):
            continue
        try:
            doc = json.loads(bundle_file.read_text())
        except Exception:
            continue
        for q in doc.get("questions", []):
            s = normalise_stem(q.get("stem") or "")
            if s:
                stem.add(s)
            tc = q.get("topic_code")
            opts = q.get("options") or []
            if tc and opts:
                first = opts[0]
                body = first.get("option_text") if isinstance(first, dict) else str(first)
                fo = normalise_option(body or "")
                if fo:
                    tfsig.add(f"{tc}|{fo}")
    return stem, tfsig


# --------------------------------------------------------------------------- #
# Batch shape + validation
# --------------------------------------------------------------------------- #

# A StaticGKBatch dict looks like::
#   {
#     "generator_tag": "claude-opus-in-chat-2026-04-19-polity-fr-batch-1",
#     "questions": [
#       {"stem": "...", "options": [{"option_text": "...", "is_correct": true}, ...],
#        "correct_letter": "C", "explanation": "...", "subject": "Polity",
#        "topic": "Fundamental Rights", "topic_code": "POL_FR",
#        "difficulty": "MEDIUM", "effort_tier": "B", "staleness_risk": 0}
#     ]
#   }

_LETTERS = ["A", "B", "C", "D", "E"]


def _validate_question(q: dict, i: int) -> List[str]:
    errs: List[str] = []
    stem = (q.get("stem") or "").strip()
    opts = q.get("options") or []
    if len(stem) < 20:
        errs.append(f"Q[{i}] stem too short ({len(stem)})")
    if len(opts) < 2:
        errs.append(f"Q[{i}] must have >= 2 options, got {len(opts)}")
    correct_count = 0
    for j, o in enumerate(opts):
        if not isinstance(o, dict):
            errs.append(f"Q[{i}].options[{j}] must be dict {{option_text, is_correct}}")
            continue
        if "option_text" not in o:
            errs.append(f"Q[{i}].options[{j}] missing option_text")
        if o.get("is_correct"):
            correct_count += 1
    if correct_count != 1:
        errs.append(f"Q[{i}] must have exactly one is_correct=True option, got {correct_count}")
    if not q.get("topic_code"):
        errs.append(f"Q[{i}] missing topic_code")
    if not q.get("subject"):
        errs.append(f"Q[{i}] missing subject")
    if q.get("staleness_risk", 0) not in (0, 1, 2):
        errs.append(f"Q[{i}] staleness_risk must be 0/1/2")
    return errs


# --------------------------------------------------------------------------- #
# Writer
# --------------------------------------------------------------------------- #

def _bundle_path(subject: str, topic_code: str) -> Path:
    subj_slug = re.sub(r"[^a-zA-Z0-9]+", "-", subject.lower()).strip("-")
    return _POOL_DIR / subj_slug / f"{topic_code}.json"


def _load_bundle(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {
        "schema_version": 1,
        "subject": None,
        "topic": None,
        "topic_code": None,
        "description": None,
        "questions": [],
    }


def apply_batch(batch: dict, dry_run: bool = False) -> dict:
    """Validate + dedup + write a batch. Returns a summary dict the caller
    prints or stores.
    """
    gen_tag = batch.get("generator_tag") or "unknown-generator"
    incoming = batch.get("questions") or []
    if not incoming:
        return {"ok": False, "reason": "empty batch"}

    tax = _load_taxonomy_and_sigs()
    pool_stem_sigs, pool_tf_sigs = _load_pool_sigs()

    validation_errs: List[str] = []
    for i, q in enumerate(incoming):
        validation_errs.extend(_validate_question(q, i))
    if validation_errs:
        return {"ok": False, "reason": "validation failed", "errors": validation_errs}

    accepted: List[dict] = []
    seen_stem_this_batch: set = set()
    seen_tf_this_batch: set = set()
    rejections: List[dict] = []

    for i, q in enumerate(incoming):
        stem_sig = normalise_stem(q.get("stem") or "")
        tc = q.get("topic_code")
        opts = q.get("options") or []
        first_body = opts[0].get("option_text", "") if opts else ""
        tf_sig = f"{tc}|{normalise_option(first_body)}"

        if stem_sig in tax.existing_stem_sigs or stem_sig in pool_stem_sigs or stem_sig in seen_stem_this_batch:
            rejections.append({"index": i, "reason": "duplicate stem signature",
                               "stem_preview": (q.get("stem") or "")[:80]})
            continue
        if tf_sig in tax.existing_topic_first_sigs or tf_sig in pool_tf_sigs or tf_sig in seen_tf_this_batch:
            rejections.append({"index": i, "reason": "duplicate (topic, first_option) signature",
                               "stem_preview": (q.get("stem") or "")[:80]})
            continue

        # Normalise — reuse the taxonomy's canonical subject/topic string if
        # the batch lacks them (so admins don't see parallel Subject strings).
        if tc in tax.by_code:
            canon = tax.by_code[tc]
            if not q.get("subject"):
                q["subject"] = canon.get("subject")
            if not q.get("topic"):
                q["topic"] = canon.get("topic")
        q.setdefault("difficulty", "MEDIUM")
        q.setdefault("effort_tier", "B")
        q.setdefault("staleness_risk", 0)
        q["answer_source"] = "generated"
        q["generator_tag"] = gen_tag
        q.setdefault("generated_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))

        seen_stem_this_batch.add(stem_sig)
        seen_tf_this_batch.add(tf_sig)
        accepted.append(q)

    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "accepted_count": len(accepted),
            "rejected_count": len(rejections),
            "rejections": rejections,
        }

    # Group accepted Qs by (subject, topic_code) and append to the right bundle.
    from collections import defaultdict
    by_bundle: Dict[tuple, List[dict]] = defaultdict(list)
    for q in accepted:
        by_bundle[(q["subject"], q["topic_code"])].append(q)

    bundle_writes: List[str] = []
    for (subj, tc), qs in by_bundle.items():
        path = _bundle_path(subj, tc)
        path.parent.mkdir(parents=True, exist_ok=True)
        bundle = _load_bundle(path)
        bundle["subject"] = subj
        bundle["topic_code"] = tc
        if qs and not bundle.get("topic"):
            bundle["topic"] = qs[0].get("topic")
        # Assign deterministic IDs
        for q in qs:
            q_seq = len(bundle["questions"]) + 1
            q.setdefault("id", f"sgk_{tc}_{q_seq:05d}")
            bundle["questions"].append(q)
        path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False))
        bundle_writes.append(str(path.relative_to(_SEEDS)))

    # Update _progress.json (generation-only count; doesn't include DB-existing)
    progress = {}
    if _PROGRESS_PATH.exists():
        progress = json.loads(_PROGRESS_PATH.read_text())
    counts = progress.get("topic_generated_counts", {})
    for q in accepted:
        counts[q["topic_code"]] = counts.get(q["topic_code"], 0) + 1
    progress["topic_generated_counts"] = counts
    progress["last_applied_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    progress["last_generator_tag"] = gen_tag
    progress["total_generated"] = sum(counts.values())
    _PROGRESS_PATH.write_text(json.dumps(progress, indent=2))

    return {
        "ok": True,
        "accepted_count": len(accepted),
        "rejected_count": len(rejections),
        "rejections": rejections,
        "bundle_writes": bundle_writes,
        "total_generated_after": progress["total_generated"],
    }


# --------------------------------------------------------------------------- #
# CLI (used for ad-hoc batch apply from JSON file)
# --------------------------------------------------------------------------- #

def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True, help="Path to a batch JSON file")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    batch = json.loads(Path(args.batch).read_text())
    result = apply_batch(batch, dry_run=args.dry_run)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
