"""Audit the seeds/pyq/ JSON corpus for two gaps the user flagged:

1. **Sanctioned-strength shortfall** — does each paper have the expected number
   of questions for its exam/stage? A short count means either (a) the parser
   lost some questions (bug) or (b) the PDF is a *section-specific* paper
   (e.g. Adda247 "English Section Memory Based" papers cover only 35–40 Qs).

2. **Missing-answer gap** — per paper, count and list the questions whose
   ``correct_index`` is ``None``. These are candidates for human (Claude-in-
   chat) solving before publication.

Emits a plain-text report to stdout and a JSON machine-readable summary to
``seeds/_audit/gaps.json``.
"""
from __future__ import annotations

import json
import logging
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

log = logging.getLogger("audit_gaps")
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

# Sanctioned total question count per (body, exam, stage) as defined by the
# official notification. Used to detect parser-induced shortfalls. See
# ``seed_exam_structure.py`` for the corresponding ExamPattern blueprints.
_SANCTIONED: Dict[Tuple[str, str, str], int] = {
    ("banks", "sbi-po", "prelims"): 100,
    ("banks", "sbi-po", "mains"): 155,
    ("banks", "ibps-po", "prelims"): 100,
    ("banks", "ibps-po", "mains"): 155,
    ("ssc", "cgl", "tier-1"): 100,
    ("ssc", "cgl", "tier-2"): 150,
    ("ssc", "chsl", "tier-1"): 100,
    ("ssc", "chsl", "tier-2"): 135,
    ("rrb", "ntpc", "cbt-1"): 100,
    ("rrb", "ntpc", "cbt-2"): 120,
}

# Filename keywords that indicate an intentionally-partial ("section-only")
# paper — its sanctioned total is NOT the full-stage count.
_SECTION_ONLY_HINTS = re.compile(
    # Match "<Subject>-Section" anywhere (e.g. "Data-Analysis-Interpretation-Section")
    # or a filename that explicitly labels itself single-subject memory-based.
    r"\-Section(?:-Memory-Based)?|"
    r"(?:Quant|English|Reasoning|Data[- ]Analysis|Computer|General[- ]Awareness)"
    r"[- ](?:Memory[- ]Based|Section)",
    re.I,
)


def _section_only_expected(filename: str) -> int | None:
    """Best-effort expected count for section-only Adda247 papers.

    These vary: English/Reasoning sections are typically 35–40, Quant 35,
    GA 40. We use a single generous lower bound (30) below which we still
    flag a shortfall.
    """
    if _SECTION_ONLY_HINTS.search(filename):
        return 30  # floor — any section paper should have at least this many
    return None


def audit(seeds_root: Path) -> dict:
    pyq_root = seeds_root / "pyq"
    results = {
        "papers_audited": 0,
        "total_questions": 0,
        "total_with_answer": 0,
        "shortfalls": [],
        "missing_answer_summary": [],
        "section_only_papers": [],
    }
    by_bucket: Dict[Tuple[str, str, str], List[dict]] = defaultdict(list)

    for json_file in sorted(pyq_root.rglob("*.json")):
        if json_file.name.startswith("_"):
            continue
        doc = json.loads(json_file.read_text())
        key = (doc["body_slug"], doc["exam_slug"], doc["stage_slug"])
        total_qs = sum(len(sec["questions"]) for sec in doc["sections"])
        with_ans = sum(
            1
            for sec in doc["sections"]
            for q in sec["questions"]
            if q["correct_index"] is not None
        )
        missing_qs = [
            {"id": q["id"], "printed_number": q["printed_number"], "subject": q["subject"], "topic": q["topic"]}
            for sec in doc["sections"]
            for q in sec["questions"]
            if q["correct_index"] is None
        ]
        results["papers_audited"] += 1
        results["total_questions"] += total_qs
        results["total_with_answer"] += with_ans

        sanctioned = _SANCTIONED.get(key, 0)
        section_floor = _section_only_expected(doc.get("source_pdf_path", "") or "")
        paper_summary = {
            "file": json_file.relative_to(seeds_root).as_posix(),
            "source_pdf": doc["source_pdf_path"],
            "body": key[0], "exam": key[1], "stage": key[2],
            "total_questions": total_qs,
            "with_correct_answer": with_ans,
            "missing_answer_count": len(missing_qs),
            "missing_answer_qs": missing_qs,
        }
        by_bucket[key].append(paper_summary)

        if section_floor is not None:
            paper_summary["section_only_expected_floor"] = section_floor
            results["section_only_papers"].append({
                "file": paper_summary["file"],
                "source_pdf": paper_summary["source_pdf"],
                "actual": total_qs,
                "expected_floor": section_floor,
                "meets_floor": total_qs >= section_floor,
            })
        elif sanctioned and total_qs < sanctioned:
            results["shortfalls"].append({
                "file": paper_summary["file"],
                "source_pdf": paper_summary["source_pdf"],
                "actual": total_qs,
                "sanctioned": sanctioned,
                "missing_count": sanctioned - total_qs,
            })

        if missing_qs:
            results["missing_answer_summary"].append({
                "file": paper_summary["file"],
                "total_questions": total_qs,
                "missing_answer_count": len(missing_qs),
            })

    results["by_bucket"] = {
        f"{b}/{e}/{s}": {
            "papers": len(ps),
            "sanctioned_per_paper": _SANCTIONED.get((b, e, s)),
            "total_questions": sum(p["total_questions"] for p in ps),
            "total_with_answer": sum(p["with_correct_answer"] for p in ps),
            "total_missing_answer": sum(p["missing_answer_count"] for p in ps),
            "papers": ps,
        }
        for (b, e, s), ps in sorted(by_bucket.items())
    }
    return results


def _render_text(report: dict) -> str:
    lines: List[str] = []
    t = report
    lines.append(f"AUDIT — {t['papers_audited']} papers, {t['total_questions']} Qs, "
                 f"{t['total_with_answer']} w/ans, "
                 f"{t['total_questions'] - t['total_with_answer']} w/o ans")
    lines.append("")

    lines.append("SHORTFALLS vs sanctioned strength (full-paper PDFs only):")
    if not t["shortfalls"]:
        lines.append("   (none — every full-paper PDF reached its sanctioned Q count)")
    for sf in t["shortfalls"]:
        lines.append(f"   {sf['file']}")
        lines.append(f"      got {sf['actual']}, sanctioned {sf['sanctioned']}, MISSING {sf['missing_count']}")
    lines.append("")

    lines.append(f"SECTION-ONLY PAPERS ({len(t['section_only_papers'])}) "
                 f"(explicitly section-specific, sanctioned count N/A):")
    for sp in t["section_only_papers"]:
        marker = "OK" if sp["meets_floor"] else "!!"
        lines.append(f"   {marker} {sp['source_pdf']}: actual={sp['actual']} floor={sp['expected_floor']}")
    lines.append("")

    lines.append(f"MISSING-ANSWER SUMMARY (papers with any unsolved Q):")
    by_bucket = t["by_bucket"]
    for bucket, data in by_bucket.items():
        if data["total_missing_answer"]:
            lines.append(f"   [{bucket}] {data['total_missing_answer']} Qs missing answer across {data['papers']} papers")
    lines.append("")

    lines.append("TOP 10 PAPERS BY MISSING-ANSWER COUNT:")
    worst = sorted(t["missing_answer_summary"], key=lambda p: -p["missing_answer_count"])[:10]
    for p in worst:
        lines.append(f"   {p['missing_answer_count']:3d} missing / {p['total_questions']:3d} total — {p['file']}")
    return "\n".join(lines)


def main() -> int:
    seeds_root = Path(__file__).resolve().parents[2] / "seeds"
    report = audit(seeds_root)
    print(_render_text(report))
    (seeds_root / "_audit").mkdir(parents=True, exist_ok=True)
    target = seeds_root / "_audit" / "gaps.json"
    target.write_text(json.dumps(report, indent=2))
    print(f"\n[JSON dump written: {target}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
