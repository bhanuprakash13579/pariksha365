"""Combine a mock blueprint + a content file of generated questions into a
canonical ``SeedTestSeries`` JSON under ``backend/seeds/mocks/...``.

Workflow
--------

1. ``scripts.mock_gen.blueprint`` produces ``mock-XX.blueprint.json`` — the
   slot-level spec (subject/topic/difficulty for each of the N questions).
2. The generator (Claude-in-chat, in a subsequent session) hand-writes
   matching ``mock-XX.content.json`` with one entry per blueprint slot,
   preserving ``order``. Each content entry supplies ``stem``, ``options``,
   ``correct_index``, ``explanation``, and any passage_context required.
3. **This script validates** the content against the blueprint (right number
   of Qs, topic/difficulty distribution adheres, correct_index in bounds,
   etc.) and emits the final ``mock-XX.json`` in the canonical
   :class:`SeedTestSeries` shape used by the DB loader.

This gives us a clean separation of concerns: the blueprint pins the
distribution (so two sessions can't produce inconsistent mocks), the content
file holds the hand-crafted questions, and the compiler enforces the
contract between them.

Content-file schema
-------------------

::

    {
      "mock_index": 1,
      "exam_slug": "sbi-po",
      "stage_slug": "prelims",
      "blueprint_path": "mock-01.blueprint.json",
      "questions": [
        {
          "order": 1,
          "stem": "...",
          "passage_context": null,
          "options": ["A-body", "B-body", "C-body", "D-body", "E-body"],
          "correct_index": 2,
          "correct_letter": "C",
          "explanation": "..."
        },
        ...
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Optional

log = logging.getLogger("mock_compile")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #

def _validate_content(blueprint: dict, content: dict) -> List[str]:
    """Return a list of human-readable error strings. Empty list = valid."""
    errs: List[str] = []

    if content.get("exam_slug") != blueprint.get("exam_slug"):
        errs.append(f"exam_slug mismatch: blueprint={blueprint['exam_slug']} content={content.get('exam_slug')}")
    if content.get("stage_slug") != blueprint.get("stage_slug"):
        errs.append(f"stage_slug mismatch: blueprint={blueprint['stage_slug']} content={content.get('stage_slug')}")
    if content.get("mock_index") != blueprint.get("mock_index"):
        errs.append(f"mock_index mismatch: blueprint={blueprint['mock_index']} content={content.get('mock_index')}")

    slots = {s["order"]: s for s in blueprint["slots"]}
    qs = content.get("questions") or []
    if len(qs) != len(slots):
        errs.append(f"question count mismatch: blueprint expects {len(slots)}, content has {len(qs)}")

    seen_orders = set()
    for q in qs:
        o = q.get("order")
        if o in seen_orders:
            errs.append(f"duplicate order={o} in content")
            continue
        seen_orders.add(o)
        slot = slots.get(o)
        if slot is None:
            errs.append(f"content has order={o} but blueprint has no such slot")
            continue
        stem = (q.get("stem") or "").strip()
        opts = q.get("options") or []
        ci = q.get("correct_index")
        if len(stem) < 10:
            errs.append(f"order {o}: stem too short ({len(stem)} chars)")
        if len(opts) < 2:
            errs.append(f"order {o}: need ≥2 options, got {len(opts)}")
        if ci is None:
            errs.append(f"order {o}: correct_index missing")
        elif not (0 <= ci < len(opts)):
            errs.append(f"order {o}: correct_index={ci} out of range for {len(opts)} options")

    missing_orders = set(slots) - seen_orders
    if missing_orders:
        errs.append(f"content missing orders: {sorted(missing_orders)}")

    return errs


# --------------------------------------------------------------------------- #
# Compile to SeedTestSeries
# --------------------------------------------------------------------------- #

_EXAM_TO_BODY = {
    "sbi-po": "banks",
    "ibps-po": "banks",
    "cgl": "ssc",
    "chsl": "ssc",
    "ntpc": "rrb",
}


def _mk_id(exam: str, stage: str, idx: int) -> str:
    return f"mock_{exam}_{stage}_{idx:02d}"


def _mk_question_id(mock_id: str, order: int) -> str:
    return f"{mock_id}_q{order:03d}"


def compile_mock(blueprint: dict, content: dict) -> dict:
    """Build the canonical SeedTestSeries dict for this mock. Callers write
    it to disk."""
    exam = blueprint["exam_slug"]
    stage = blueprint["stage_slug"]
    idx = blueprint["mock_index"]
    mock_id = _mk_id(exam, stage, idx)

    # Group blueprint slots by section
    sections_by_order: Dict[int, dict] = {}
    for s in blueprint["sections"]:
        sections_by_order[s["order"]] = {
            "name": s["name"],
            "subject": s["subject"],
            "order": s["order"],
            "time_limit_minutes": s.get("duration_minutes"),
            "marks_per_question": s.get("marks_per_question", 1.0),
            "questions": [],
        }

    content_by_order = {q["order"]: q for q in content["questions"]}

    for slot in blueprint["slots"]:
        q = content_by_order[slot["order"]]
        sq = {
            "id": _mk_question_id(mock_id, slot["order"]),
            "stem": q["stem"].strip(),
            "passage_context": (q.get("passage_context") or None),
            "options": [o.strip() for o in q["options"]],
            "correct_index": q["correct_index"],
            "correct_letter": q.get("correct_letter"),
            "explanation": q.get("explanation"),
            "subject": slot["subject"],
            "topic": slot["topic"],
            "topic_code": slot["topic_code_hint"],
            "difficulty": slot["difficulty"],
            "answer_source": "generated",
            "staleness_risk": 0,
            "images": [],
            "source_pdf_path": None,
            "source_page_range": None,
            "printed_number": slot["order"],
            "parse_issues": [],
        }
        sections_by_order[slot["section_order"]]["questions"].append(sq)

    sections = [sections_by_order[i] for i in sorted(sections_by_order)]
    all_qs = [q for s in sections for q in s["questions"]]

    out = {
        "schema_version": 1,
        "id": mock_id,
        "title": f"{exam.upper().replace('-', ' ')} {stage.replace('-', ' ').title()} — Mock {idx:02d}",
        "description": (
            f"Predictive mock test #{idx} for {exam.upper()} {stage}, generated from "
            f"PYQ topic-frequency analysis. Static GA only (no current affairs)."
        ),
        "test_type": "MOCK",
        "body_slug": _EXAM_TO_BODY.get(exam, "unknown"),
        "exam_slug": exam,
        "stage_slug": stage,
        "total_duration_minutes": blueprint["total_duration_minutes"],
        "negative_marking": blueprint["negative_mark"],
        "has_sectional_timing": blueprint["has_sectional_timing"],
        "source_pdf_path": None,
        "source_format": None,
        "paper_date": None,
        "paper_shift": None,
        "parse_health": {
            "total_questions": len(all_qs),
            "with_correct_answer": sum(1 for q in all_qs if q["correct_index"] is not None),
            "with_explanation": sum(1 for q in all_qs if q.get("explanation")),
            "with_images": 0,
            "unparsed_pages": [],
            "paper_issues": [],
        },
        "sections": sections,
    }
    return out


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--blueprint", required=True, help="Path to mock-XX.blueprint.json")
    ap.add_argument("--content", required=True, help="Path to mock-XX.content.json")
    ap.add_argument("--out", required=True, help="Output path for mock-XX.json")
    args = ap.parse_args()

    bp = json.loads(Path(args.blueprint).read_text())
    ct = json.loads(Path(args.content).read_text())
    errs = _validate_content(bp, ct)
    if errs:
        log.error("content failed validation (%d issues):", len(errs))
        for e in errs:
            log.error("  • %s", e)
        return 2
    out = compile_mock(bp, ct)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=2, ensure_ascii=False))
    log.info("compiled %s → %s (%d Qs)", args.blueprint, args.out, out["parse_health"]["total_questions"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
