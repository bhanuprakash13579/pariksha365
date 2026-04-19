"""Export the "unsolved" questions from ``seeds/pyq/**/*.json`` into compact
per-paper queue files at ``seeds/_solve_queue/<body>/<exam>/<stage>/<paper-stem>.queue.json``.

Two types of rows end up in each queue:

* **solvable** — the parser got the stem and all options; we just need a correct
  answer + short explanation. These are what I (Claude in chat) can fill in
  directly across a few batches.
* **unextractable** — the stem or options are missing/very short, typically
  because the question lived on an image-only page. These get a
  ``needs_ocr=true`` flag and are skipped by the in-chat solver.

The queue file is the *input* to the solver workflow; solutions are written
back via ``apply_solutions.py`` into the original seed JSONs, setting
``answer_source="generated"`` so admins can audit which answers came from a
model rather than a PDF answer key.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import List

log = logging.getLogger("export_solve_queue")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def _is_unextractable(question: dict) -> bool:
    """Decide whether a Q needs OCR (skip it from the solver queue) or is
    solvable from text alone.
    """
    stem = (question.get("stem") or "").strip()
    options = question.get("options") or []
    if len(stem) < 20:
        return True
    if len(options) < 2:
        return True
    # Options with near-empty text are a sign of image-only page cross-contamination.
    if sum(1 for o in options if len((o or "").strip()) < 2) > 0:
        return True
    return False


def export(seeds_root: Path, out_root: Path) -> int:
    pyq_root = seeds_root / "pyq"
    out_root.mkdir(parents=True, exist_ok=True)
    totals = {
        "papers_scanned": 0,
        "total_missing": 0,
        "solvable": 0,
        "needs_ocr": 0,
        "queue_files_written": 0,
    }
    for json_file in sorted(pyq_root.rglob("*.json")):
        if json_file.name.startswith("_"):
            continue
        doc = json.loads(json_file.read_text())
        totals["papers_scanned"] += 1
        unsolved: List[dict] = []
        for sec in doc["sections"]:
            for q in sec["questions"]:
                if q.get("correct_index") is not None:
                    continue
                entry = {
                    "question_id": q["id"],
                    "printed_number": q.get("printed_number"),
                    "subject": q.get("subject"),
                    "topic": q.get("topic"),
                    "difficulty_guess": q.get("difficulty"),
                    "passage_context": q.get("passage_context"),
                    "stem": q.get("stem") or "",
                    "options": q.get("options") or [],
                    "source_page_range": q.get("source_page_range"),
                    "needs_ocr": _is_unextractable(q),
                }
                if entry["needs_ocr"]:
                    totals["needs_ocr"] += 1
                else:
                    totals["solvable"] += 1
                totals["total_missing"] += 1
                unsolved.append(entry)
        if not unsolved:
            continue
        rel = json_file.relative_to(pyq_root)
        target = out_root / rel.with_suffix(".queue.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps({
            "paper_id": doc["id"],
            "paper_title": doc["title"],
            "source_pdf_path": doc.get("source_pdf_path"),
            "body_slug": doc["body_slug"],
            "exam_slug": doc["exam_slug"],
            "stage_slug": doc["stage_slug"],
            "total_unsolved": len(unsolved),
            "solvable": sum(1 for u in unsolved if not u["needs_ocr"]),
            "needs_ocr": sum(1 for u in unsolved if u["needs_ocr"]),
            "questions": unsolved,
        }, indent=2, ensure_ascii=False))
        totals["queue_files_written"] += 1

    # Master index
    (out_root / "_queue_index.json").write_text(json.dumps(totals, indent=2))
    log.info("queue export complete: %s", totals)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    seeds_default = str(Path(__file__).resolve().parents[2] / "seeds")
    ap.add_argument("--seeds", default=seeds_default)
    args = ap.parse_args()
    seeds_root = Path(args.seeds).expanduser().resolve()
    out_root = seeds_root / "_solve_queue"
    return export(seeds_root, out_root)


if __name__ == "__main__":
    sys.exit(main())
