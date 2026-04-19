"""Write the 71 parsed PYQ PDFs to the canonical seed JSON format.

Walks ``~/Documents/pariksha``, dispatches each PDF through the parser +
classifier, extracts question-relevant images (filtering branding via xref
frequency), and writes one JSON per paper under
``backend/seeds/pyq/<body>/<exam>/<stage>/<pdf-stem>.json``, plus a
flat ``backend/seeds/pyq/_index.json``.

The on-disk schema is defined in :mod:`seed_schema`; see that module for the
contract the DB loader (Phase LOAD) will consume.

Image extraction details
------------------------
PyMuPDF exposes every image object on a page along with its bounding box.
A typical Adda247 paper carries 60–500 images per file, but 95 % of them are
branding: the Adda247 logo, page-number box, and URL watermark embedded on
every page. We distinguish "real figures" from branding using two heuristics:

1. **xref frequency** — an image xref that appears on ≥ 50 % of pages is
   almost certainly branding and is dropped.
2. **minimum footprint** — an image smaller than 60 × 30 px at 150 DPI
   (roughly a postage stamp) is dropped — thumbs and tick icons.

The survivors are written out to ``backend/seeds/images/<pdf-sha1>/p{N}-img{M}.<ext>``
and associated with the question whose stem Y-position is closest on that page.

Run from ``backend/``::

    python -m scripts.pyq_ingest.seed_writer --root ~/Documents/pariksha
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import logging
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz

from scripts.pyq_ingest.classifier import classify_paper
from scripts.pyq_ingest.parser import ParsedPaper, ParsedQuestion, parse_paper
from scripts.pyq_ingest.seed_schema import (
    SCHEMA_VERSION,
    QuestionImage,
    SeedIndex,
    SeedIndexEntry,
    SeedQuestion,
    SeedSection,
    SeedTestSeries,
)
from scripts.pyq_ingest.topic_codes import get_topic_code
from scripts.pyq_ingest.topic_frequency import assign_bucket

log = logging.getLogger("seed_writer")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s | %(message)s")


# --------------------------------------------------------------------------- #
# Path / slug helpers
# --------------------------------------------------------------------------- #

_EXAM_TO_BODY = {
    "SBI PO": "banks",
    "IBPS PO": "banks",
    "CGL": "ssc",
    "CHSL": "ssc",
    "NTPC": "rrb",
}
_EXAM_TO_SLUG = {
    "SBI PO": "sbi-po",
    "IBPS PO": "ibps-po",
    "CGL": "cgl",
    "CHSL": "chsl",
    "NTPC": "ntpc",
}
# Per (exam_slug, stage_slug): (total_duration_min, has_sectional_timing, neg_mark)
# Mirrors what the seed_exam_structure script inserts for ExamPattern; the loader
# will cross-check rather than blindly trust this, but we embed it so the JSON
# files are self-contained for review without a DB.
_STAGE_META: Dict[Tuple[str, str], Tuple[int, bool, float]] = {
    ("sbi-po", "prelims"): (60, True, 0.25),
    ("sbi-po", "mains"): (180, True, 0.25),
    ("ibps-po", "prelims"): (60, True, 0.25),
    ("ibps-po", "mains"): (180, True, 0.25),
    ("cgl", "tier-1"): (60, False, 0.5),
    ("cgl", "tier-2"): (135, True, 1.0),
    ("chsl", "tier-1"): (60, False, 0.5),
    ("chsl", "tier-2"): (135, True, 1.0),
    ("ntpc", "cbt-1"): (90, False, 0.3333),
    ("ntpc", "cbt-2"): (90, False, 0.3333),
}


def _slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s or "unknown"


def _file_sha1(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _build_question_id(pdf_sha: str, printed_number: Optional[int], monotonic: int) -> str:
    """Deterministic ID for a PYQ question — re-ingest produces the same ID so
    the loader's upsert is a no-op.
    """
    num_tag = f"p{printed_number}" if printed_number is not None else f"m{monotonic}"
    return f"pyq_{pdf_sha}_{num_tag}"


def _build_paper_id(pdf_sha: str) -> str:
    return f"pyq_paper_{pdf_sha}"


# --------------------------------------------------------------------------- #
# Paper-title + date extraction from filename (best effort)
# --------------------------------------------------------------------------- #

_DATE_IN_NAME = re.compile(
    r"(?P<d>\d{1,2})[-_ ]?(?P<m>[A-Za-z]{3}|\d{1,2})[-_ ]?(?P<y>20\d{2})"
)
_SHIFT_IN_NAME = re.compile(r"(Shift[-_ ]*\d|[1-4][a-z]{2}[-_ ]*[Ss]hift)")


def _extract_paper_meta(pdf_path: Path) -> Tuple[str, Optional[dt.date], Optional[str]]:
    stem = pdf_path.stem.replace("_", " ").replace("-", " ")
    title = stem
    paper_date: Optional[dt.date] = None
    shift: Optional[str] = None

    m = _DATE_IN_NAME.search(pdf_path.stem)
    if m:
        try:
            day = int(m.group("d"))
            y = int(m.group("y"))
            mo_raw = m.group("m")
            if mo_raw.isdigit():
                mo = int(mo_raw)
            else:
                mo = {
                    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
                }.get(mo_raw[:3].lower(), 0)
            if 1 <= mo <= 12 and 1 <= day <= 31:
                paper_date = dt.date(y, mo, day)
        except Exception:
            pass

    m2 = _SHIFT_IN_NAME.search(pdf_path.stem)
    if m2:
        shift = m2.group(0).replace("-", " ").replace("_", " ").strip()

    return title, paper_date, shift


# --------------------------------------------------------------------------- #
# Image extraction
# --------------------------------------------------------------------------- #

def _collect_page_images(
    doc: fitz.Document,
) -> Tuple[Dict[int, List[Tuple[int, tuple]]], Counter]:
    """Return ``({page_index: [(xref, rect_tuple), ...]}, xref_frequency_counter)``.

    ``rect_tuple`` is ``(x0, y0, x1, y1)``. Not all embedded images have a
    usable rect (rare edge case); those are skipped.
    """
    by_page: Dict[int, List[Tuple[int, tuple]]] = {}
    freq: Counter = Counter()
    for i in range(len(doc)):
        page = doc[i]
        entries: List[Tuple[int, tuple]] = []
        for img in page.get_images(full=True):
            xref = img[0]
            try:
                rects = page.get_image_rects(xref)
            except Exception:
                rects = []
            if not rects:
                continue
            r = rects[0]
            entries.append((xref, (r.x0, r.y0, r.x1, r.y1)))
            freq[xref] += 1
        by_page[i] = entries
    return by_page, freq


def _is_branding(xref: int, rect: tuple, freq: Counter, total_pages: int) -> bool:
    """Reject images we're confident aren't question figures."""
    # Branding heuristic: the same xref appears on ≥ 50 % of pages
    if freq[xref] >= max(2, total_pages // 2):
        return True
    x0, y0, x1, y1 = rect
    w = max(0.0, x1 - x0)
    h = max(0.0, y1 - y0)
    # Postage-stamp filter
    if w < 60 and h < 30:
        return True
    return False


def _save_page_image(
    doc: fitz.Document,
    page_idx: int,
    xref: int,
    out_dir: Path,
    serial: int,
) -> Optional[QuestionImage]:
    """Extract raw image bytes for ``xref`` and write them to ``out_dir``. Returns
    the metadata record (relative path, size) or ``None`` on failure.
    """
    try:
        pix = fitz.Pixmap(doc, xref)
        # RGB+alpha → strip alpha; CMYK → convert to RGB
        if pix.n >= 5:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        out_dir.mkdir(parents=True, exist_ok=True)
        filename = f"p{page_idx + 1}-img{serial}.png"
        target = out_dir / filename
        pix.save(str(target))
        rel = target.relative_to(out_dir.parent.parent).as_posix()
        return QuestionImage(path=rel, width=pix.width, height=pix.height)
    except Exception as e:
        log.warning("failed to save image xref=%d on page %d: %s", xref, page_idx + 1, e)
        return None


def _associate_images_with_questions(
    paper_questions: List[ParsedQuestion],
    page_images: Dict[int, List[QuestionImage]],
) -> Dict[int, List[QuestionImage]]:
    """Return ``{question_order: [images]}`` — a per-page round-robin
    assignment of images to questions on that same page.

    This is intentionally approximate: the parser doesn't retain per-question
    y-coordinates, so we can't do strict "nearest stem above" matching.
    In practice SSC/RRB papers have at most 1-2 figure images per page (plus
    branding that's already filtered out), and Adda247 papers use almost no
    inline figures — so the round-robin error is small and easy to review.
    Unattached images (questions on their page weren't parsed) are logged by
    the caller but still written to disk.
    """
    out: Dict[int, List[QuestionImage]] = defaultdict(list)
    by_page: Dict[int, List[ParsedQuestion]] = defaultdict(list)
    for q in paper_questions:
        by_page[q.page_start].append(q)

    for page_1based, images in page_images.items():
        candidates = by_page.get(page_1based, [])
        if not candidates or not images:
            continue
        # Preserve relative order of images (already sorted by reading position
        # in _collect_page_images) — distribute roughly evenly across questions.
        for i, img_meta in enumerate(images):
            idx = min(i * len(candidates) // max(1, len(images)), len(candidates) - 1)
            out[candidates[idx].order].append(img_meta)
    return out


# --------------------------------------------------------------------------- #
# PDF → SeedTestSeries
# --------------------------------------------------------------------------- #

def _paper_to_seed(
    pdf_path: Path,
    root: Path,
    out_seeds_dir: Path,
    body_slug: str,
    exam_slug: str,
    stage_slug: str,
    exam_label: str,
    stage_label: str,
) -> Tuple[SeedTestSeries, dict]:
    paper = parse_paper(str(pdf_path))
    classified = classify_paper(paper, exam_label=exam_label, stage_label=stage_label)

    pdf_sha = _file_sha1(pdf_path)
    img_out_dir = out_seeds_dir / "images" / pdf_sha

    # Image extraction
    doc = fitz.open(pdf_path)
    by_page, xref_freq = _collect_page_images(doc)
    kept_per_page: Dict[int, List[QuestionImage]] = defaultdict(list)
    rects_per_page: Dict[int, List[tuple]] = defaultdict(list)
    serial = 0
    for page_idx, entries in by_page.items():
        for xref, rect in entries:
            if _is_branding(xref, rect, xref_freq, len(doc)):
                continue
            serial += 1
            img = _save_page_image(doc, page_idx, xref, img_out_dir, serial)
            if img is None:
                continue
            kept_per_page[page_idx + 1].append(img)
            rects_per_page[page_idx + 1].append(rect)
    doc.close()

    attach_map = _associate_images_with_questions(paper.questions, kept_per_page)

    # Build seed questions
    classified_by_order = {c.order: c for c in classified}
    seed_questions: List[SeedQuestion] = []
    for q in paper.questions:
        meta = classified_by_order.get(q.order)
        subject = meta.subject if meta else "UNCLASSIFIED"
        topic = meta.topic if meta and meta.topic != "UNCLASSIFIED" else None
        difficulty = meta.difficulty_guess if meta else "MEDIUM"
        sq = SeedQuestion(
            id=_build_question_id(pdf_sha, q.printed_number, q.order),
            stem=q.stem.strip(),
            passage_context=q.passage_context.strip() if q.passage_context else None,
            options=[o.strip() for o in q.options],
            correct_index=q.correct_index,
            correct_letter=q.correct_letter,
            explanation=q.explanation,
            subject=subject,
            topic=topic,
            topic_code=get_topic_code(subject, topic or ""),
            difficulty=difficulty,  # type: ignore[arg-type]
            answer_source="pdf_extracted",
            staleness_risk=0,
            images=attach_map.get(q.order, []),
            source_pdf_path=str(pdf_path.relative_to(root)),
            source_page_range=[q.page_start, q.page_end],
            printed_number=q.printed_number,
            parse_issues=q.issues,
        )
        seed_questions.append(sq)

    # All PYQ questions go into a single section (the original paper structure
    # is section-less in the parser; mock tests and the loader's optional
    # post-processor can split per ExamPattern if desired).
    total_duration, sectional, neg = _STAGE_META.get(
        (exam_slug, stage_slug), (60, False, 0.0)
    )
    title, paper_date, paper_shift = _extract_paper_meta(pdf_path)

    section = SeedSection(
        name="Full Paper",
        subject="MIXED",
        order=1,
        time_limit_minutes=total_duration,
        marks_per_question=1.0,
        questions=seed_questions,
    )

    series = SeedTestSeries(
        id=_build_paper_id(pdf_sha),
        title=title.title(),
        description=f"Previous-year paper from {pdf_path.name}",
        test_type="PYQ",
        body_slug=body_slug,
        exam_slug=exam_slug,
        stage_slug=stage_slug,
        total_duration_minutes=total_duration,
        negative_marking=neg,
        has_sectional_timing=sectional,
        source_pdf_path=str(pdf_path.relative_to(root)),
        source_format=paper.source_format,
        paper_date=paper_date,
        paper_shift=paper_shift,
        parse_health={
            "total_questions": len(seed_questions),
            "with_correct_answer": sum(1 for q in seed_questions if q.correct_index is not None),
            "with_explanation": sum(1 for q in seed_questions if q.explanation),
            "with_images": sum(1 for q in seed_questions if q.images),
            "unparsed_pages": paper.unparsed_pages,
            "paper_issues": paper.issues,
        },
        sections=[section],
    )
    return series, series.parse_health


# --------------------------------------------------------------------------- #
# Walk corpus → write seeds/
# --------------------------------------------------------------------------- #

def run(corpus_root: Path, seeds_root: Path) -> int:
    seeds_root.mkdir(parents=True, exist_ok=True)
    index: List[SeedIndexEntry] = []
    totals = {"papers": 0, "questions": 0, "with_answer": 0, "with_images": 0, "skipped": 0}

    for pdf_path in sorted(corpus_root.rglob("*.pdf")):
        bucket = assign_bucket(str(pdf_path))
        if bucket is None:
            totals["skipped"] += 1
            log.warning("skip (no bucket): %s", pdf_path.relative_to(corpus_root))
            continue
        exam_label, stage_label = bucket
        body_slug = _EXAM_TO_BODY.get(exam_label, "unknown")
        exam_slug = _EXAM_TO_SLUG.get(exam_label, _slugify(exam_label))
        stage_slug = stage_label  # already slug-shaped from topic_frequency

        series, health = _paper_to_seed(
            pdf_path, corpus_root, seeds_root,
            body_slug, exam_slug, stage_slug,
            exam_label, stage_label,
        )

        out_dir = seeds_root / "pyq" / body_slug / exam_slug / stage_slug
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / f"{pdf_path.stem}.json"
        out_file.write_text(series.model_dump_json(indent=2))

        totals["papers"] += 1
        totals["questions"] += health["total_questions"]
        totals["with_answer"] += health["with_correct_answer"]
        totals["with_images"] += health["with_images"]

        index.append(SeedIndexEntry(
            file=str(out_file.relative_to(seeds_root)),
            title=series.title,
            test_type="PYQ",
            body_slug=body_slug,
            exam_slug=exam_slug,
            stage_slug=stage_slug,
            questions=health["total_questions"],
        ))
        log.info(
            "wrote %-50s  (%3d Qs, %3d w/ans, %3d w/img)",
            out_file.relative_to(seeds_root),
            health["total_questions"],
            health["with_correct_answer"],
            health["with_images"],
        )

    idx_doc = SeedIndex(
        schema_version=SCHEMA_VERSION,
        generated_at=dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        entries=index,
    )
    (seeds_root / "pyq" / "_index.json").write_text(idx_doc.model_dump_json(indent=2))
    log.info("Index written. Totals: %s", totals)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="~/Documents/pariksha", help="PDF corpus root")
    ap.add_argument(
        "--seeds",
        default=str(Path(__file__).resolve().parents[2] / "seeds"),
        help="Output seeds root (default: backend/seeds)",
    )
    args = ap.parse_args()
    corpus_root = Path(args.root).expanduser().resolve()
    seeds_root = Path(args.seeds).expanduser().resolve()
    if not corpus_root.exists():
        log.error("corpus root does not exist: %s", corpus_root)
        return 2
    return run(corpus_root, seeds_root)


if __name__ == "__main__":
    sys.exit(main())
