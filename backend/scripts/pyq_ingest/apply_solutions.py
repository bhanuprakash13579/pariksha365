"""Apply a batch of solved-answer patches back into ``seeds/pyq/**/*.json``.

Workflow:

1. ``export_solve_queue.py`` writes per-paper queue files listing unsolved Qs.
2. The solver (Claude in chat) reads a queue file, generates
   :class:`AnswerPatch` records, and writes them to
   ``seeds/_solutions/<body>__<exam>__<stage>__<paper-stem>.solutions.json``.
3. This script reads every ``*.solutions.json`` file and merges its patches
   into the matching seed JSON, setting ``answer_source="generated"`` and
   appending the explanation. Missing patches are logged but not fatal —
   partial batches are fine.

Idempotency: patches include the ``question_id`` (deterministic from source
PDF + printed number), so re-running the applier against the same solutions
file is a safe no-op.
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field

log = logging.getLogger("apply_solutions")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")


class AnswerPatch(BaseModel):
    """One solved answer for a specific question.

    ``staleness_risk`` is optional — set to 2 on PYQ questions that happen to
    ask about current affairs (RBI actions, specific scheme dates, recent
    appointments) so they are excluded from weak-topic practice flows even
    while remaining in the archived paper. Leave ``None`` to keep whatever
    the seed JSON already has (usually 0).
    """

    question_id: str
    correct_index: int = Field(ge=0, le=9)
    correct_letter: str
    explanation: str
    confidence: float = Field(default=0.9, ge=0, le=1)
    solved_by: str = "claude-opus-in-chat"
    staleness_risk: int | None = Field(default=None, ge=0, le=2)

    model_config = ConfigDict(extra="forbid")


class SolutionsBatch(BaseModel):
    """A batch of solved patches. Typically one per paper, produced by the
    solver reading one ``*.queue.json``.
    """

    paper_id: str
    source_pdf_path: str | None = None
    patches: List[AnswerPatch]

    model_config = ConfigDict(extra="forbid")


def apply_batch(seeds_root: Path, batch: SolutionsBatch) -> dict:
    """Merge one solutions batch into the matching seed paper JSON.

    Returns counters: ``{matched: int, missed: int, already_solved: int}``.
    """
    # Find the paper json by paper_id
    by_id = {}
    for p in (seeds_root / "pyq").rglob("*.json"):
        if p.name.startswith("_"):
            continue
        doc = json.loads(p.read_text())
        by_id[doc["id"]] = (p, doc)
    if batch.paper_id not in by_id:
        log.error("no paper found for id=%s", batch.paper_id)
        return {"matched": 0, "missed": len(batch.patches), "already_solved": 0, "error": "paper_not_found"}

    target_path, doc = by_id[batch.paper_id]
    patches_by_qid: Dict[str, AnswerPatch] = {p.question_id: p for p in batch.patches}

    matched = 0
    already = 0
    for sec in doc["sections"]:
        for q in sec["questions"]:
            patch = patches_by_qid.pop(q["id"], None)
            if patch is None:
                continue
            if q.get("correct_index") is not None:
                already += 1
                continue
            if not (0 <= patch.correct_index < len(q.get("options") or [])):
                log.warning(
                    "patch for %s has correct_index=%d but paper has %d options — skipping",
                    q["id"], patch.correct_index, len(q.get("options") or []),
                )
                continue
            q["correct_index"] = patch.correct_index
            q["correct_letter"] = patch.correct_letter
            if patch.explanation:
                q["explanation"] = patch.explanation
            q["answer_source"] = "generated"
            if patch.staleness_risk is not None:
                q["staleness_risk"] = patch.staleness_risk
            matched += 1

    # Refresh paper-level counters so they agree with the patched questions.
    all_qs = [q for sec in doc["sections"] for q in sec["questions"]]
    doc["parse_health"] = {
        "total_questions": len(all_qs),
        "with_correct_answer": sum(1 for q in all_qs if q.get("correct_index") is not None),
        "with_explanation": sum(1 for q in all_qs if q.get("explanation")),
        "with_images": sum(1 for q in all_qs if q.get("images")),
        "unparsed_pages": doc.get("parse_health", {}).get("unparsed_pages", []),
        "paper_issues": doc.get("parse_health", {}).get("paper_issues", []),
    }

    target_path.write_text(json.dumps(doc, indent=2, ensure_ascii=False))
    missed = list(patches_by_qid.keys())
    if missed:
        log.warning("patches with no matching question: %s", missed)
    return {"matched": matched, "missed": len(missed), "already_solved": already}


def apply_all(seeds_root: Path) -> int:
    sol_dir = seeds_root / "_solutions"
    if not sol_dir.exists():
        log.error("no _solutions dir at %s", sol_dir)
        return 2
    totals = {"files_applied": 0, "matched": 0, "missed": 0, "already_solved": 0}
    for f in sorted(sol_dir.glob("*.solutions.json")):
        batch = SolutionsBatch.model_validate_json(f.read_text())
        res = apply_batch(seeds_root, batch)
        log.info("%s → %s", f.name, res)
        if "error" in res:
            continue
        totals["files_applied"] += 1
        totals["matched"] += res["matched"]
        totals["missed"] += res["missed"]
        totals["already_solved"] += res["already_solved"]
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
