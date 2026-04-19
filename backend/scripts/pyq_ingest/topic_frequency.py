"""Aggregate per-exam topic-frequency tables from the PYQ corpus.

Walks ``~/Documents/pariksha`` (or any directory passed via ``--root``),
assigns each PDF to an (exam, stage) bucket based on its path, parses it,
classifies each question, and emits a per-bucket JSON report:

    {
      "exam": "CGL",
      "stage": "tier-1",
      "papers_analyzed": 9,
      "total_questions": 900,
      "parse_health": {
          "with_correct_answer": 870,
          "unclassified_subject": 5,
          "unclassified_topic": 120,
          "with_parse_issues": 23
      },
      "by_subject": {
        "REASONING": {
          "count": 225,
          "avg_per_paper": 25.0,
          "difficulty_mix": {"EASY": 40, "MEDIUM": 160, "HARD": 25},
          "topics": {
             "coding_decoding": {"count": 18, "share_pct": 8.0, ...},
             ...
          }
        },
        ...
      },
      "papers": [
         {"path": "...", "questions": 100, "with_answer": 91, ...},
         ...
      ]
    }

These JSONs are the source of truth for the mock-test generator in Phase 3:
each new mock picks subject → topic → difficulty according to the empirical
distribution so the generated paper mirrors the real exam's taste.

Run::

    python -m scripts.pyq_ingest.topic_frequency \
        --root ~/Documents/pariksha --out /tmp/topic_frequency

No external network dependency; pure PyMuPDF + stdlib.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from scripts.pyq_ingest.classifier import ClassifiedQuestion, classify_paper
from scripts.pyq_ingest.parser import parse_paper

log = logging.getLogger("topic_frequency")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s | %(message)s")

# --------------------------------------------------------------------------- #
# Path → (exam, stage) mapping
# --------------------------------------------------------------------------- #
# The corpus uses inconsistent casing ("Mains" vs "mains", "Tier-1" vs "Tier 1")
# so we normalise via regexes rather than literal-string matches.

_PATH_RULES: List[Tuple[re.Pattern, str, str]] = [
    (re.compile(r"/Banks/SBI[ _-]*PO/[^/]*(?:prelim|pre)", re.I), "SBI PO", "prelims"),
    (re.compile(r"/Banks/SBI[ _-]*PO/[^/]*(?:main)", re.I), "SBI PO", "mains"),
    (re.compile(r"/Banks/IBPS[ _-]*PO/[^/]*(?:prelim|pre)", re.I), "IBPS PO", "prelims"),
    (re.compile(r"/Banks/IBPS[ _-]*PO/[^/]*(?:main)", re.I), "IBPS PO", "mains"),
    (re.compile(r"/cgl/[^/]*tier[ _-]*1", re.I), "CGL", "tier-1"),
    (re.compile(r"/cgl/[^/]*tier[ _-]*2", re.I), "CGL", "tier-2"),
    (re.compile(r"/chsl/[^/]*tier[ _-]*1", re.I), "CHSL", "tier-1"),
    (re.compile(r"/chsl/[^/]*tier[ _-]*2", re.I), "CHSL", "tier-2"),
    (re.compile(r"/RRB/NTPC/[^/]*CBT[ _-]*1", re.I), "NTPC", "cbt-1"),
    (re.compile(r"/RRB/NTPC/[^/]*CBT[ _-]*2", re.I), "NTPC", "cbt-2"),
]


def assign_bucket(pdf_path: str) -> Optional[Tuple[str, str]]:
    for rx, exam, stage in _PATH_RULES:
        if rx.search(pdf_path):
            return exam, stage
    return None


# --------------------------------------------------------------------------- #
# Aggregation
# --------------------------------------------------------------------------- #

def _collect_bucket_rows(root: Path) -> Dict[Tuple[str, str], List[Path]]:
    """Group all .pdf files under ``root`` by (exam, stage) bucket."""
    buckets: Dict[Tuple[str, str], List[Path]] = defaultdict(list)
    skipped: List[Path] = []
    for pdf in sorted(root.rglob("*.pdf")):
        key = assign_bucket(str(pdf))
        if key is None:
            skipped.append(pdf)
            continue
        buckets[key].append(pdf)
    if skipped:
        log.warning("%d PDFs didn't match any (exam, stage) rule:", len(skipped))
        for p in skipped[:20]:
            log.warning("  skipped: %s", p)
    return buckets


def _aggregate_bucket(
    exam: str, stage: str, pdfs: List[Path]
) -> dict:
    """Parse + classify every paper in a bucket and roll up to the report shape.

    All counts are integers; shares are rounded to one decimal place for
    readability but the raw counts are what mock-generation consumes.
    """
    paper_infos = []
    all_classified: List[ClassifiedQuestion] = []

    for pdf in pdfs:
        paper = parse_paper(str(pdf))
        rows = classify_paper(paper, exam_label=exam, stage_label=stage)
        paper_infos.append({
            "path": str(pdf),
            "source_format": paper.source_format,
            "questions": len(paper.questions),
            "with_correct_answer": sum(
                1 for q in paper.questions if q.correct_index is not None
            ),
            "unparsed_pages": paper.unparsed_pages,
            "paper_issues": paper.issues,
        })
        all_classified.extend(rows)

    by_subject: Dict[str, dict] = {}
    parse_health = {
        "with_correct_answer": sum(1 for c in all_classified if c.has_correct_answer),
        "unclassified_subject": sum(
            1 for c in all_classified if c.subject == "UNCLASSIFIED"
        ),
        "unclassified_topic": sum(
            1 for c in all_classified if c.topic == "UNCLASSIFIED"
        ),
        "with_parse_issues": sum(1 for c in all_classified if c.issues),
    }

    # Group by subject and topic
    subject_groups: Dict[str, List[ClassifiedQuestion]] = defaultdict(list)
    for row in all_classified:
        subject_groups[row.subject].append(row)

    total = len(all_classified)
    for subject, rows in subject_groups.items():
        topic_groups: Dict[str, List[ClassifiedQuestion]] = defaultdict(list)
        for r in rows:
            topic_groups[r.topic].append(r)

        topic_stats: Dict[str, dict] = {}
        for topic, trs in sorted(
            topic_groups.items(), key=lambda kv: -len(kv[1])
        ):
            diff = Counter(r.difficulty_guess for r in trs)
            topic_stats[topic] = {
                "count": len(trs),
                "share_of_subject_pct": round(100 * len(trs) / max(1, len(rows)), 1),
                "avg_per_paper": round(len(trs) / max(1, len(pdfs)), 2),
                "difficulty_mix": dict(diff),
                "unique_stems_preview": [r.stem_preview for r in trs[:3]],
            }

        by_subject[subject] = {
            "count": len(rows),
            "share_of_paper_pct": round(100 * len(rows) / max(1, total), 1),
            "avg_per_paper": round(len(rows) / max(1, len(pdfs)), 2),
            "difficulty_mix": dict(Counter(r.difficulty_guess for r in rows)),
            "topics": topic_stats,
        }

    return {
        "exam": exam,
        "stage": stage,
        "papers_analyzed": len(pdfs),
        "total_questions": total,
        "parse_health": parse_health,
        "by_subject": dict(
            sorted(by_subject.items(), key=lambda kv: -kv[1]["count"])
        ),
        "papers": paper_infos,
    }


def run(root: Path, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    buckets = _collect_bucket_rows(root)
    if not buckets:
        log.error("No PDFs matched any bucket rule under %s", root)
        return 2
    grand_summary = []
    for (exam, stage), pdfs in sorted(buckets.items()):
        log.info("Processing %s / %s (%d papers)", exam, stage, len(pdfs))
        report = _aggregate_bucket(exam, stage, pdfs)
        safe_exam = exam.lower().replace(" ", "-")
        target = out_dir / f"{safe_exam}__{stage}.json"
        target.write_text(json.dumps(report, indent=2))
        grand_summary.append({
            "file": target.name,
            "exam": exam, "stage": stage,
            "papers": report["papers_analyzed"],
            "questions": report["total_questions"],
            "with_answer": report["parse_health"]["with_correct_answer"],
            "unclassified_topic": report["parse_health"]["unclassified_topic"],
        })
        log.info(
            "  wrote %s  (%d Qs, %d with answers, %d unclassified topics)",
            target.name, report["total_questions"],
            report["parse_health"]["with_correct_answer"],
            report["parse_health"]["unclassified_topic"],
        )
    (out_dir / "_index.json").write_text(json.dumps(grand_summary, indent=2))
    log.info("Index written: %s", out_dir / "_index.json")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="~/Documents/pariksha", help="PDF corpus root")
    ap.add_argument("--out", default="/tmp/topic_frequency", help="Output directory for JSON reports")
    args = ap.parse_args()
    root = Path(args.root).expanduser().resolve()
    out = Path(args.out).expanduser().resolve()
    if not root.exists():
        log.error("Corpus root does not exist: %s", root)
        return 2
    return run(root, out)


if __name__ == "__main__":
    sys.exit(main())
