"""Recover questions from image-only pages via OCR + green-pixel detection.

The PYQ corpus has 367 questions that live on pages where the PDF's text layer
is empty or near-empty — typically SSC/RRB official papers that export certain
pages as rasterised images. These pages still carry the green-coloured
"correct-answer" highlight in pixels, but our first-pass parser (which relies
on text-span colours) can't see them.

This module runs a second pass that:

1. Walks every seed JSON in ``backend/seeds/pyq/`` and collects the
   ``unparsed_pages`` list from each paper's ``parse_health``.
2. For each flagged page, renders the page to PNG at 300 DPI using PyMuPDF,
   runs it through OCR_module's GOT-OCR 2.0 engine (locally cached, free),
   and — in the same rasterised image — scans for the signature
   rgb(64, 198, 75) green pixels that mark the correct option.
3. Parses the OCR output into ``Q.N``-style questions + option tuples and
   emits a per-paper recovery file under
   ``backend/seeds/_ocr_recovered/<paper-stem>.recovered.json`` in the same
   schema the main seed writer uses.

A separate merger (:mod:`apply_ocr_recovery`) inserts the new question
records into the seed JSONs and refreshes ``parse_health`` counters. This
two-step design lets an admin review OCR output before it hits the canonical
seeds — important because GOT-OCR occasionally garbles formulas.

Run from the backend directory::

    /home/bhanu/Desktop/OCR_module/.venv/bin/python -m scripts.pyq_ingest.ocr_recover \\
        --pyq-corpus ~/Documents/pariksha \\
        [--only <paper-stem>]      # debug flag for single-paper runs
        [--max-pages N]            # cap for smoke-testing

The script **must** be run with OCR_module's venv because it pulls in torch
+ transformers + the GOT-OCR weights. The main parsing scripts continue to
work with the lighter PyMuPDF-only venv.
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from dataclasses import dataclass, field, asdict
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import numpy as np
from PIL import Image

log = logging.getLogger("ocr_recover")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s | %(message)s")

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

RENDER_DPI = 300                    # PDF → PNG render resolution
GREEN_TARGET = np.array([64, 198, 75], dtype=np.int16)  # SSC/RRB correct-answer highlight
GREEN_TOLERANCE = 35                # per-channel tolerance around the target rgb
MIN_GREEN_BLOB_PX = 40              # reject specks; a real "C. 1670" has hundreds of green px


# --------------------------------------------------------------------------- #
# Green-pixel detection
# --------------------------------------------------------------------------- #

@dataclass
class GreenRegion:
    """A contiguous run of green pixels on the rendered page — one per
    correct-answer option in the typical SSC/RRB layout."""
    y_center: float   # normalised 0..1 (top=0, bottom=1)
    x_center: float
    px_count: int


def detect_green_regions(img_rgb: np.ndarray) -> List[GreenRegion]:
    """Return the Y-ordered list of green-pixel clusters on the page.

    We don't do proper connected-components labelling (overkill for
    per-option detection); instead we:

    * Build a boolean mask of ``|pixel - GREEN_TARGET| <= GREEN_TOLERANCE``
      across RGB channels.
    * Collapse the mask rowwise to find Y-bands with ≥ MIN_GREEN_BLOB_PX of
      green pixels.
    * Within each band, report the centroid as a ``GreenRegion``.
    """
    diff = np.abs(img_rgb.astype(np.int16) - GREEN_TARGET).max(axis=2)
    mask = diff <= GREEN_TOLERANCE
    row_counts = mask.sum(axis=1)
    h, w = mask.shape

    regions: List[GreenRegion] = []
    in_band = False
    band_start = 0
    for y in range(h):
        is_green = row_counts[y] >= 4  # a real green option line spans many pixels horizontally
        if is_green and not in_band:
            band_start = y
            in_band = True
        elif not is_green and in_band:
            band_end = y
            band_mask = mask[band_start:band_end]
            px_count = int(band_mask.sum())
            if px_count >= MIN_GREEN_BLOB_PX:
                ys, xs = np.where(band_mask)
                if len(ys):
                    cy = float((ys.mean() + band_start)) / h
                    cx = float(xs.mean()) / w
                    regions.append(GreenRegion(y_center=cy, x_center=cx, px_count=px_count))
            in_band = False
    if in_band:
        band_end = h
        band_mask = mask[band_start:band_end]
        px_count = int(band_mask.sum())
        if px_count >= MIN_GREEN_BLOB_PX:
            ys, xs = np.where(band_mask)
            if len(ys):
                cy = float((ys.mean() + band_start)) / h
                cx = float(xs.mean()) / w
                regions.append(GreenRegion(y_center=cy, x_center=cx, px_count=px_count))

    regions.sort(key=lambda r: r.y_center)
    return regions


# --------------------------------------------------------------------------- #
# OCR output parser
# --------------------------------------------------------------------------- #

# GOT-OCR output with mode='format' preserves line breaks but strips exotic
# formatting. We expect question blocks shaped like::
#
#     Q.17
#     The Sultan of Delhi who ...
#     Ans
#     1. Balban
#     2. Iltutmish
#     3. Alauddin Khilji
#     4. Qutbuddin Aibak
#
# SSC uses ``1./2./3./4.`` numbering; RRB uses ``A./B./C./D.``. The parser
# accepts both and falls back to producing lower-confidence output if the
# layout is mangled.

_Q_HEAD = re.compile(r"^\s*Q\.?\s*(\d+)\s*$")
_OPT_SSC = re.compile(r"^\s*([1-4])[\.\)]\s*(.+)$")
_OPT_RRB = re.compile(r"^\s*([A-D])[\.\)]\s*(.+)$")


@dataclass
class RecoveredQuestion:
    """One question recovered from an OCR pass."""
    printed_number: int
    stem: str
    options: List[str]
    option_letters: List[str]       # matches options, e.g. ["1","2","3","4"] or ["A","B","C","D"]
    # Filled later by matching green regions to options (see
    # ``attach_correct_from_regions``).
    correct_index: Optional[int] = None
    correct_letter: Optional[str] = None
    source_page: int = 0
    issues: List[str] = field(default_factory=list)


def parse_ocr_text(text: str) -> List[RecoveredQuestion]:
    """Walk OCR output line-by-line and bucket into questions.

    State machine identical to the SSC/RRB official parser we already wrote,
    but operating on text produced by the OCR engine. Kept deliberately
    lenient — we accept questions with 2-5 options and leave options-missing
    cases on the record so the admin merger can see them.
    """
    out: List[RecoveredQuestion] = []
    current: Optional[RecoveredQuestion] = None
    state = "IDLE"

    def flush():
        nonlocal current
        if current is not None:
            out.append(current)
        current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        m = _Q_HEAD.match(line)
        if m:
            flush()
            current = RecoveredQuestion(
                printed_number=int(m.group(1)),
                stem="",
                options=[],
                option_letters=[],
            )
            state = "STEM"
            continue
        if current is None:
            continue
        if line.strip().lower() in ("ans", "ans."):
            state = "OPTIONS"
            continue
        if state == "STEM":
            current.stem = (current.stem + " " + line).strip() if current.stem else line
        elif state == "OPTIONS":
            m1 = _OPT_SSC.match(line) or _OPT_RRB.match(line)
            if m1:
                current.option_letters.append(m1.group(1))
                current.options.append(m1.group(2).strip())
            elif current.options:
                # option wrapped to next line — tack it on
                current.options[-1] = (current.options[-1] + " " + line).strip()
    flush()
    for q in out:
        if not q.options:
            q.issues.append("no options parsed from OCR")
    return out


def attach_correct_from_regions(
    questions: List[RecoveredQuestion],
    regions: List[GreenRegion],
) -> None:
    """For each recovered question we assume its options occupy the lower
    half of the page in reading order. Match each green region to the
    nearest option-index slot by Y position.

    This is a rough matcher. The page's 4 options are laid out in equal
    vertical bands below the stem; we split the [question_y_start,
    page_bottom] range into N_options slots and assign each region to the
    slot that contains its y_center. A question with no matching green
    region stays ``correct_index=None``.
    """
    if not regions or not questions:
        return
    # Single-question page is the common SSC/RRB case. Multi-question pages
    # are less common but still possible when the paper is densely laid out.
    if len(questions) == 1:
        q = questions[0]
        if not q.options:
            return
        # The green region nearest the vertical middle of the options is the
        # correct one. Since we don't know exactly where options start, use
        # the first region as a proxy (SSC/RRB papers show exactly one green
        # per correct answer per question).
        r = regions[0]
        # Map region to option by evenly dividing 0..1 across N options
        # assuming options start around y=0.4 on the page.
        n = len(q.options)
        # fraction of the lower 60% of the page
        local = (r.y_center - 0.30) / 0.65
        idx = max(0, min(n - 1, int(local * n)))
        q.correct_index = idx
        q.correct_letter = q.option_letters[idx] if idx < len(q.option_letters) else None
        return

    # Multi-question page: assign each region to the nearest question, then
    # pick the best option within that question by relative y-position.
    q_centers = np.linspace(0.1, 0.9, len(questions))  # approximate
    for r in regions:
        q_idx = int(np.argmin(np.abs(q_centers - r.y_center)))
        q = questions[q_idx]
        if not q.options:
            continue
        local = (r.y_center - (q_centers[q_idx] - 0.05)) / 0.1
        idx = max(0, min(len(q.options) - 1, int(local * len(q.options))))
        q.correct_index = idx
        q.correct_letter = q.option_letters[idx] if idx < len(q.option_letters) else None


# --------------------------------------------------------------------------- #
# Seed-JSON walker — finds targets to OCR
# --------------------------------------------------------------------------- #

@dataclass
class OCRTarget:
    """One page slated for OCR recovery."""
    paper_json: Path
    paper_id: str
    source_pdf: Path
    pdf_sha: str         # 16-char hash used as the paper identifier
    page_numbers: List[int]


def discover_targets(seeds_root: Path, corpus_root: Path) -> List[OCRTarget]:
    """Scan ``seeds/pyq/**/*.json`` for papers whose ``parse_health.unparsed_pages``
    is non-empty, and resolve each one to the on-disk source PDF.
    """
    targets: List[OCRTarget] = []
    for jf in sorted((seeds_root / "pyq").rglob("*.json")):
        if jf.name.startswith("_"):
            continue
        doc = json.loads(jf.read_text())
        unparsed = doc.get("parse_health", {}).get("unparsed_pages") or []
        if not unparsed:
            continue
        src_rel = doc.get("source_pdf_path")
        if not src_rel:
            continue
        src = corpus_root / src_rel
        if not src.exists():
            log.warning("source PDF missing for %s: %s", jf.name, src)
            continue
        # The pdf_sha is the middle token of the paper id e.g. "pyq_paper_<sha>"
        pid = doc["id"]
        sha = pid.replace("pyq_paper_", "")
        targets.append(OCRTarget(
            paper_json=jf, paper_id=pid, source_pdf=src,
            pdf_sha=sha, page_numbers=unparsed,
        ))
    return targets


# --------------------------------------------------------------------------- #
# Main orchestration
# --------------------------------------------------------------------------- #

def render_page_rgb(pdf: fitz.Document, page_index: int, dpi: int = RENDER_DPI) -> np.ndarray:
    """Render one PDF page to a contiguous RGB numpy array at the given DPI."""
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    page = pdf[page_index]
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    return np.asarray(img, dtype=np.uint8)


def run(
    seeds_root: Path,
    corpus_root: Path,
    output_dir: Path,
    only_paper: Optional[str] = None,
    max_pages: Optional[int] = None,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = discover_targets(seeds_root, corpus_root)
    if only_paper:
        targets = [t for t in targets if only_paper in t.source_pdf.name]
    log.info("%d papers have image-only pages to OCR", len(targets))
    if not targets:
        log.warning("nothing to do")
        return 0

    # Import OCR engine lazily so the module stays importable even when torch
    # isn't available (e.g. for IDE autocomplete or --help).
    sys.path.insert(0, "/home/bhanu/Desktop/OCR_module")
    from ocr_module.engines.got_ocr import GOTOCREngine

    log.info("loading GOT-OCR model (cached @ ~/.cache/huggingface/)")
    engine = GOTOCREngine()
    log.info("model loaded on device=%s", engine.device)

    grand_total_pages = 0
    total_recovered_qs = 0

    for t in targets:
        doc = fitz.open(t.source_pdf)
        recovered: List[RecoveredQuestion] = []
        page_records = []

        for page_no in t.page_numbers:
            if max_pages is not None and grand_total_pages >= max_pages:
                break
            page_idx = page_no - 1
            if not (0 <= page_idx < len(doc)):
                continue

            img_rgb = render_page_rgb(doc, page_idx)
            pil_img = Image.fromarray(img_rgb)

            try:
                text = engine.extract(pil_img, mode="format")
            except Exception as e:
                log.warning("OCR failed on %s page %d: %s", t.source_pdf.name, page_no, e)
                continue

            regions = detect_green_regions(img_rgb)
            page_qs = parse_ocr_text(text)
            for q in page_qs:
                q.source_page = page_no
            attach_correct_from_regions(page_qs, regions)

            recovered.extend(page_qs)
            page_records.append({
                "page": page_no,
                "ocr_chars": len(text),
                "green_regions": len(regions),
                "questions_recovered": len(page_qs),
            })
            grand_total_pages += 1

        doc.close()

        if recovered:
            out = output_dir / f"{t.source_pdf.stem}.recovered.json"
            out.write_text(json.dumps({
                "paper_id": t.paper_id,
                "source_pdf": str(t.source_pdf.relative_to(corpus_root)),
                "pdf_sha": t.pdf_sha,
                "ocr_engine": "stepfun-ai/GOT-OCR-2.0-hf",
                "pages_processed": page_records,
                "questions": [asdict(q) for q in recovered],
            }, indent=2, ensure_ascii=False))
            total_recovered_qs += len(recovered)
            log.info(
                "wrote %s  (%d Qs across %d pages)",
                out.relative_to(seeds_root),
                len(recovered), len(page_records),
            )
        else:
            log.warning("no questions recovered from %s", t.source_pdf.name)

        if max_pages is not None and grand_total_pages >= max_pages:
            log.info("reached --max-pages=%d, stopping early", max_pages)
            break

    log.info(
        "done — %d papers, %d pages OCRed, %d questions recovered",
        len(targets), grand_total_pages, total_recovered_qs,
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    seeds_default = str(Path(__file__).resolve().parents[2] / "seeds")
    ap.add_argument("--seeds", default=seeds_default)
    ap.add_argument("--pyq-corpus", default="~/Documents/pariksha",
                    help="Root of the source PDFs (for resolving source_pdf_path)")
    ap.add_argument("--output-dir", default=None,
                    help="Where to write recovery JSONs (default: seeds/_ocr_recovered)")
    ap.add_argument("--only", default=None,
                    help="Substring match on paper filename — debug flag for single-paper runs")
    ap.add_argument("--max-pages", type=int, default=None,
                    help="Stop after processing N pages — smoke-test flag")
    args = ap.parse_args()

    seeds_root = Path(args.seeds).expanduser().resolve()
    corpus_root = Path(args.pyq_corpus).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else seeds_root / "_ocr_recovered"
    if not corpus_root.exists():
        log.error("corpus root missing: %s", corpus_root)
        return 2
    return run(seeds_root, corpus_root, output_dir, args.only, args.max_pages)


if __name__ == "__main__":
    sys.exit(main())
