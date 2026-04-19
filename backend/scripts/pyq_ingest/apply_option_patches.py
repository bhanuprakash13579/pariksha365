"""Apply OCR-recovered option patches (from :mod:`ocr_recover_options`) to the
canonical seed JSONs.

Reads every ``seeds/_ocr_options/*.options.json`` file, looks up each patch's
``question_id`` in the appropriate paper, and fills in:
  * ``options`` — replaces the empty/tiny option bodies with OCR-extracted text
  * ``correct_index`` / ``correct_letter`` — if the green-pixel detector tagged one
  * ``answer_source`` — set to ``"pdf_extracted"`` when green detection
    supplied the correct answer (it came from the paper's own highlight),
    ``"generated"`` otherwise (we filled options but still need a solver
    pass to mark the right one).

Idempotency: patches are keyed by deterministic ``question_id``, so reruns are
no-ops once applied.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

log = logging.getLogger("apply_option_patches")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


def _load_paper_index(seeds_root: Path) -> Dict[str, Path]:
    """Map paper_id → seed JSON path."""
    out: Dict[str, Path] = {}
    for p in (seeds_root / "pyq").rglob("*.json"):
        if p.name.startswith("_"):
            continue
        doc = json.loads(p.read_text())
        out[doc["id"]] = p
    return out


def apply_all(seeds_root: Path) -> int:
    options_dir = seeds_root / "_ocr_options"
    if not options_dir.exists():
        log.error("no _ocr_options dir at %s", options_dir)
        return 2
    paper_index = _load_paper_index(seeds_root)
    totals = {"files_applied": 0, "options_filled": 0, "correct_tagged": 0, "skipped": 0}

    for patch_file in sorted(options_dir.glob("*.options.json")):
        batch = json.loads(patch_file.read_text())
        paper_path = paper_index.get(batch["paper_id"])
        if paper_path is None:
            log.warning("no matching paper for %s", patch_file.name)
            continue
        doc = json.loads(paper_path.read_text())
        patches_by_qid = {p["question_id"]: p for p in batch["patches"]}

        for sec in doc["sections"]:
            for q in sec["questions"]:
                patch = patches_by_qid.get(q["id"])
                if patch is None:
                    continue
                # Always overwrite option bodies — the parser's extraction was known-bad
                if patch.get("options"):
                    q["options"] = patch["options"]
                if "correct_index" in patch:
                    if q.get("correct_index") is None:
                        q["correct_index"] = patch["correct_index"]
                        q["correct_letter"] = patch["correct_letter"]
                        # Correct answer came from the paper's green highlight
                        q["answer_source"] = "pdf_extracted"
                        totals["correct_tagged"] += 1
                # Clear stale parser_issues that referenced missing options
                q["parse_issues"] = [
                    i for i in q.get("parse_issues", [])
                    if "no options parsed" not in i and "only 0 options parsed" not in i
                ]
                totals["options_filled"] += 1

        # Refresh parse_health
        all_qs = [q for sec in doc["sections"] for q in sec["questions"]]
        doc["parse_health"] = {
            "total_questions": len(all_qs),
            "with_correct_answer": sum(1 for q in all_qs if q.get("correct_index") is not None),
            "with_explanation": sum(1 for q in all_qs if q.get("explanation")),
            "with_images": sum(1 for q in all_qs if q.get("images")),
            "unparsed_pages": doc.get("parse_health", {}).get("unparsed_pages", []),
            "paper_issues": doc.get("parse_health", {}).get("paper_issues", []),
        }
        paper_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
        totals["files_applied"] += 1
        log.info(
            "%s → filled options for %d Qs, green-tagged %d",
            paper_path.name,
            sum(1 for p in batch["patches"] if p["question_id"] in {q["id"] for sec in doc["sections"] for q in sec["questions"]}),
            sum(1 for p in batch["patches"] if "correct_index" in p),
        )

    log.info("applied all: %s", totals)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    seeds_default = str(Path(__file__).resolve().parents[2] / "seeds")
    ap.add_argument("--seeds", default=seeds_default)
    args = ap.parse_args()
    return apply_all(Path(args.seeds).expanduser().resolve())


if __name__ == "__main__":
    sys.exit(main())
