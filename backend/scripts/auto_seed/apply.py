"""Accept a generated bundle, run all gates, merge into canonical pool.

Usage:
    python3 -m scripts.auto_seed.apply path/to/bundle.json
    python3 -m scripts.auto_seed.apply path/to/bundle.json --dry-run

The bundle JSON can be in Schema A or B. apply() normalises to Schema A
and writes the canonical file at:
    seeds/static_gk/<subject_folder>/<TOPIC_CODE>.json

If that file already exists, the new questions are appended (with id
renumbering) — never overwrite an existing bundle.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .canonical import SUBJECT_FOLDER, to_schema_a_bundle
from .gates import run_all_gates

_BACKEND = Path(__file__).resolve().parents[2]
_POOL = _BACKEND / "seeds" / "static_gk"


def _bundle_path(subject: str, topic_code: str) -> Path:
    folder = SUBJECT_FOLDER.get(subject)
    if not folder:
        raise ValueError(f"no folder mapping for subject {subject!r}")
    return _POOL / folder / f"{topic_code}.json"


def _load_or_new_bundle(path: Path, subject: str, topic: str, topic_code: str) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {
        "schema_version": 1,
        "subject": subject,
        "topic": topic,
        "topic_code": topic_code,
        "questions": [],
    }


def _next_id_for(topic_code: str, existing_count: int) -> str:
    return f"sgk_{topic_code}_{existing_count + 1:05d}"


def apply(bundle: dict, dry_run: bool = False, generator_tag: str | None = None) -> dict:
    rep = run_all_gates(bundle)
    if not rep["ok"]:
        return {
            "ok": False,
            "reason": "gate failure",
            "gates": {k: v for k, v in rep["results"].items() if not v["ok"]},
        }
    norm = rep["normalised_bundle"]
    subject = norm["subject"]
    topic = norm["topic"]
    topic_code = norm["topic_code"]

    out_path = _bundle_path(subject, topic_code)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    existing = _load_or_new_bundle(out_path, subject, topic, topic_code)
    if not existing.get("topic"):
        existing["topic"] = topic
    existing["subject"] = subject  # canonicalise on every write
    existing["topic_code"] = topic_code

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    tag = generator_tag or f"auto-seed-{now[:10]}"

    added: list[str] = []
    for q in norm["questions"]:
        q.setdefault("answer_source", "generated")
        q.setdefault("generator_tag", tag)
        q.setdefault("generated_at", now)
        q["id"] = _next_id_for(topic_code, len(existing["questions"]))
        existing["questions"].append(q)
        added.append(q["id"])

    summary = {
        "ok": True,
        "topic_code": topic_code,
        "subject": subject,
        "topic": topic,
        "path": str(out_path.relative_to(_BACKEND)),
        "added_ids": added,
        "total_after": len(existing["questions"]),
    }

    if dry_run:
        summary["dry_run"] = True
        return summary

    out_path.write_text(json.dumps(existing, indent=2, ensure_ascii=False))
    return summary


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("file", help="bundle JSON to ingest")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()
    bundle = json.loads(Path(args.file).read_text())
    res = apply(bundle, dry_run=args.dry_run, generator_tag=args.tag)
    print(json.dumps(res, indent=2, ensure_ascii=False)[:2000])
    return 0 if res.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
