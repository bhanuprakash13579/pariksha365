"""OCR pass #2 — recover option BODIES and correct-answer marks for questions
whose stems parsed cleanly but whose options are rendered as image glyphs in
the PDF (typical of SSC CHSL Tier-II papers with ₹ currency options or CGL
papers with mathematical expressions as options).

These pages are NOT flagged as ``unparsed_pages`` — their text layer is fine;
it just contains ``1.`` / ``2.`` / ``3.`` / ``4.`` with empty bodies. OCR
pass #1 (:mod:`ocr_recover`) missed them because it only targeted pages
with near-empty text extraction.

Pipeline:

1. Scan every seed JSON for questions where:
     * ``correct_index`` is None
     * ``stem`` is ≥ 20 chars (so we know the Q itself exists)
     * every option's body is shorter than 3 characters (the ``N.`` prefix
       extracted fine but the body is image glyphs)
   Group those Qs by (paper, page).
2. For each (paper, page), render the page at 300 DPI, run GOT-OCR to
   extract the full text, parse the `Q.N ... 1. body / 2. body / 3. body
   / 4. body` structure, and also scan the rendered page for green pixels
   (SSC/RRB correct-answer markers).
3. Emit one ``*.options.json`` patch file per paper containing:
     * updated option texts keyed by question_id
     * recovered ``correct_index`` + ``correct_letter`` where the green
       detector found a clear winner
4. A companion merger (:mod:`apply_option_patches`) applies these patches
   to the seed JSONs.

Run (requires OCR_module's venv)::

    /home/bhanu/Desktop/OCR_module/.venv/bin/python \\
        -m scripts.pyq_ingest.ocr_recover_options \\
        [--only <paper-stem>] [--max-pages N]
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz
import numpy as np
from PIL import Image

from scripts.pyq_ingest.ocr_recover import (
    GREEN_TARGET,
    GREEN_TOLERANCE,
    MIN_GREEN_BLOB_PX,
    RENDER_DPI,
    GreenRegion,
    detect_green_regions,
    render_page_rgb,
)

log = logging.getLogger("ocr_options")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s | %(message)s")


# --------------------------------------------------------------------------- #
# Target discovery
# --------------------------------------------------------------------------- #

@dataclass
class TargetQuestion:
    """A Q whose option bodies need OCR recovery."""
    question_id: str
    printed_number: int
    stem_preview: str       # first 80 chars for logging
    current_options: List[str]   # what the parser extracted (mostly empty strings)


@dataclass
class TargetPage:
    """One page on which we run OCR, possibly containing multiple targets."""
    pdf_path: Path
    paper_json: Path
    paper_id: str
    page_number: int         # 1-based
    questions: List[TargetQuestion]


def _option_bodies_missing(q: dict) -> bool:
    """True when stem parsed cleanly but every option body is empty or
    near-empty (≤ 2 chars) — signature of image-rendered option glyphs."""
    stem = (q.get("stem") or "").strip()
    if len(stem) < 20:
        return False
    opts = q.get("options") or []
    if not opts:
        return True
    return all(len((o or "").strip()) <= 2 for o in opts)


def discover_option_recovery_targets(seeds_root: Path, corpus_root: Path) -> List[TargetPage]:
    """Scan seed JSONs and collect every page whose questions need option OCR."""
    by_page: Dict[Tuple[Path, Path, str, int], List[TargetQuestion]] = defaultdict(list)
    for jf in sorted((seeds_root / "pyq").rglob("*.json")):
        if jf.name.startswith("_"):
            continue
        doc = json.loads(jf.read_text())
        src_rel = doc.get("source_pdf_path")
        if not src_rel:
            continue
        src = corpus_root / src_rel
        if not src.exists():
            continue
        for sec in doc["sections"]:
            for q in sec["questions"]:
                if q.get("correct_index") is not None:
                    continue
                if not _option_bodies_missing(q):
                    continue
                pr = q.get("source_page_range") or []
                if not pr:
                    continue
                page_no = pr[0]
                key = (src, jf, doc["id"], page_no)
                by_page[key].append(TargetQuestion(
                    question_id=q["id"],
                    printed_number=q.get("printed_number") or 0,
                    stem_preview=(q.get("stem") or "")[:80],
                    current_options=q.get("options") or [],
                ))
    return [
        TargetPage(pdf_path=src, paper_json=jf, paper_id=pid, page_number=pn, questions=qs)
        for (src, jf, pid, pn), qs in by_page.items()
    ]


# --------------------------------------------------------------------------- #
# OCR parsing for options
# --------------------------------------------------------------------------- #

# GOT-OCR returns LaTeX-flavoured output. Question headings may be ``Q. 7`` or
# ``Q.7`` (sometimes with a space before the number). Options appear delimited
# by the option number followed by a comma (``1,body``) — NOT a period — because
# the source PDF renders the option-number + body together as a single glyph,
# and OCR often reads the rendered dot as a comma. Correct answers carry a
# leading ``\square`` sigil (representing the green-highlighted checkbox in
# the source); wrong options carry ``\mathrm{X}``.
_Q_HEAD = re.compile(r"^\s*Q\.?\s*(\d+)[\s.]*(.*)$")
_OPT_LATEX = re.compile(
    r"([\\](?:square|mathrm\{X\}))?\s*(?:\(\s*)?\s*([1-4])\s*[,.]\s*(.+?)\s*(?:\\\))?\s*$"
)
# Strip standalone LaTeX wrappers we don't care about
_LATEX_NOISE = re.compile(r"\\(?:quad|qquad|;|,|:|!)\s*")
_METADATA_DROP = re.compile(
    r"^(Question ID|Option \d ID|Status|Chosen Option|SubQuestion No|www\.|Section :|Copyright)",
    re.I,
)
_METADATA_NUMERIC_ID = re.compile(r"^\d{8,}$")


def _clean_latex(s: str) -> str:
    """Strip LaTeX spacing commands and math-mode delimiters from an option
    body so the merger stores clean text."""
    s = s.replace("\\(", "").replace("\\)", "")
    s = _LATEX_NOISE.sub(" ", s)
    # Convert \frac{a}{b} to a/b for readability — do this BEFORE stripping
    # other backslash commands, since the \frac name would otherwise be eaten
    # and we'd lose the fraction structure.
    s = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"(\1/\2)", s)
    # Drop remaining solitary LaTeX command names like \mathrm, \square, \text, \rm
    s = re.sub(r"\\(?:mathrm|mathit|mathbf|rm|it|bf|text|operatorname)\s*\{([^{}]*)\}", r"\1", s)
    # Drop any remaining \commandname (but NOT \frac — already handled above)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    s = s.replace("{", "").replace("}", "")
    return re.sub(r"\s{2,}", " ", s).strip()


@dataclass
class OCRedQuestion:
    """Question parsed from OCR output — what we'll merge back."""
    printed_number: int
    stem: str
    options: List[str]
    option_letters: List[str]
    correct_index: Optional[int] = None
    correct_letter: Optional[str] = None


def _split_option_line(line: str) -> List[Tuple[str, str, bool]]:
    """A single OCR line can contain multiple options packed together — the
    engine sometimes concatenates all four options on the ``Ans`` line. Split
    on the ``\\(mathrm{X})|\\(square)`` markers and the leading digit to
    isolate each option tuple ``(letter, body, is_correct)``.
    """
    # Tokenize by the LaTeX option markers
    chunks = re.split(r"(\\square|\\mathrm\{X\})", line)
    out: List[Tuple[str, str, bool]] = []
    pending_correct = False
    for piece in chunks:
        piece = piece.strip()
        if piece == "\\square":
            pending_correct = True
            continue
        if piece == "\\mathrm{X}":
            pending_correct = False
            continue
        # Look for option letter/number at the start of the chunk
        m = re.match(r"^\s*\(?\s*([1-4A-D])\s*[,.]\s*(.+?)\s*(?:\\\)|$)", piece)
        if m:
            out.append((m.group(1), _clean_latex(m.group(2)), pending_correct))
            pending_correct = False
    return out


def _parse_ocr_questions(text: str) -> List[OCRedQuestion]:
    """Parse GOT-OCR output into questions + options.

    Handles both ``Q. N`` (with intra-line stem) and plain ``Q.N`` headers.
    Option bodies may arrive on individual lines OR all packed on the ``Ans``
    line — :func:`_split_option_line` handles the latter case.
    """
    out: List[OCRedQuestion] = []
    current: Optional[OCRedQuestion] = None
    state = "IDLE"

    def flush():
        nonlocal current
        if current is not None and (current.stem or current.options):
            out.append(current)
        current = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if _METADATA_DROP.match(line) or _METADATA_NUMERIC_ID.match(line):
            if state == "OPTIONS":
                state = "SEALED"
            continue

        mq = _Q_HEAD.match(line)
        if mq:
            flush()
            current = OCRedQuestion(
                printed_number=int(mq.group(1)),
                stem=_clean_latex(mq.group(2)) if mq.group(2) else "",
                options=[],
                option_letters=[],
            )
            state = "STEM"
            continue

        if current is None:
            continue

        # The "Ans" line often carries option(s) inline; treat it as both.
        if line.lower().startswith("ans"):
            state = "OPTIONS"
            line = re.sub(r"^\s*Ans\s*\.?\s*", "", line, flags=re.I).strip()
            if not line:
                continue

        if state == "STEM":
            current.stem = (current.stem + " " + _clean_latex(line)).strip() if current.stem else _clean_latex(line)
            continue

        if state == "OPTIONS":
            pieces = _split_option_line(line)
            if pieces:
                for letter, body, is_correct in pieces:
                    if body:
                        current.option_letters.append(letter)
                        current.options.append(body)
                        if is_correct:
                            current.correct_index = len(current.options) - 1
                            current.correct_letter = letter
                continue
            # Fallback: treat as continuation of last option
            if current.options:
                current.options[-1] = (current.options[-1] + " " + _clean_latex(line)).strip()

    flush()
    # Dedup options while preserving order (OCR sometimes repeats)
    for q in out:
        seen = set()
        uniq_opts: List[str] = []
        uniq_letters: List[str] = []
        for opt, letter in zip(q.options, q.option_letters):
            key = (letter, opt[:40])
            if key in seen:
                continue
            seen.add(key)
            uniq_opts.append(opt)
            uniq_letters.append(letter)
        q.options = uniq_opts
        q.option_letters = uniq_letters
    return out


def _attach_correct_from_regions(
    q: OCRedQuestion, regions: List[GreenRegion], page_height_band: Tuple[float, float] | None = None
) -> None:
    """Simple heuristic: if exactly one green region on the page, map it to
    an option by its relative Y. More robust than the naive approach in
    :mod:`ocr_recover` because here we usually have exactly one Q per page
    when options are image-rendered.
    """
    if not q.options or not regions:
        return
    # Take the most prominent green region (highest pixel count) on the page
    r = max(regions, key=lambda g: g.px_count)
    n = len(q.options)
    # Options occupy the lower 2/3 of the page approximately; map proportionally
    local = (r.y_center - 0.30) / 0.70
    idx = max(0, min(n - 1, int(local * n)))
    q.correct_index = idx
    if idx < len(q.option_letters):
        q.correct_letter = q.option_letters[idx]


# --------------------------------------------------------------------------- #
# Orchestrator
# --------------------------------------------------------------------------- #

def run(
    seeds_root: Path,
    corpus_root: Path,
    output_dir: Path,
    only_paper: Optional[str] = None,
    max_pages: Optional[int] = None,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = discover_option_recovery_targets(seeds_root, corpus_root)
    if only_paper:
        targets = [t for t in targets if only_paper in t.pdf_path.name]

    log.info(
        "discovered %d page-level targets across %d papers (total %d Qs awaiting option OCR)",
        len(targets),
        len({t.paper_id for t in targets}),
        sum(len(t.questions) for t in targets),
    )
    if not targets:
        return 0

    # Lazy-load the heavy OCR engine so module import stays cheap.
    sys.path.insert(0, "/home/bhanu/Desktop/OCR_module")
    from ocr_module.engines.got_ocr import GOTOCREngine

    log.info("loading GOT-OCR (first run only — model cached at ~/.cache/huggingface/)")
    engine = GOTOCREngine()
    log.info("model loaded on device=%s", engine.device)

    # Group targets by PDF for batched page access
    by_pdf: Dict[Path, List[TargetPage]] = defaultdict(list)
    for t in targets:
        by_pdf[t.pdf_path].append(t)

    total_pages = 0
    total_options_recovered = 0
    total_correct_tagged = 0

    for pdf_path, pages in by_pdf.items():
        doc = fitz.open(pdf_path)
        paper_id = pages[0].paper_id
        patches_by_qid: Dict[str, dict] = {}

        for page_target in pages:
            if max_pages is not None and total_pages >= max_pages:
                break
            page_idx = page_target.page_number - 1
            if not (0 <= page_idx < len(doc)):
                continue

            img_rgb = render_page_rgb(doc, page_idx)
            pil = Image.fromarray(img_rgb)
            try:
                text = engine.extract(pil, mode="format")
            except Exception as e:
                log.warning("OCR failed on %s page %d: %s", pdf_path.name, page_target.page_number, e)
                continue
            regions = detect_green_regions(img_rgb)
            ocr_qs = _parse_ocr_questions(text)
            # Index OCR-recovered Qs by printed_number
            ocr_by_num = {oq.printed_number: oq for oq in ocr_qs}

            for tq in page_target.questions:
                oq = ocr_by_num.get(tq.printed_number)
                if oq is None or not oq.options:
                    continue
                # Map green regions to option if the page has only this one Q
                # actively needing recovery — otherwise skip green detection
                # (multi-Q pages are ambiguous).
                if len(page_target.questions) == 1:
                    _attach_correct_from_regions(oq, regions)
                patch = {
                    "question_id": tq.question_id,
                    "options": oq.options,
                    "option_letters": oq.option_letters,
                    "ocr_stem_preview": oq.stem[:120],
                }
                if oq.correct_index is not None:
                    patch["correct_index"] = oq.correct_index
                    patch["correct_letter"] = oq.correct_letter
                    total_correct_tagged += 1
                patches_by_qid[tq.question_id] = patch
                total_options_recovered += 1

            total_pages += 1

        doc.close()

        if patches_by_qid:
            out_file = output_dir / f"{pdf_path.stem}.options.json"
            out_file.write_text(json.dumps({
                "paper_id": paper_id,
                "source_pdf": str(pdf_path.relative_to(corpus_root)),
                "ocr_engine": "stepfun-ai/GOT-OCR-2.0-hf",
                "patches": list(patches_by_qid.values()),
            }, indent=2, ensure_ascii=False))
            log.info(
                "wrote %s (%d Q patches, %d with correct answer)",
                out_file.name,
                len(patches_by_qid),
                sum(1 for p in patches_by_qid.values() if "correct_index" in p),
            )

        if max_pages is not None and total_pages >= max_pages:
            log.info("reached --max-pages=%d — stopping", max_pages)
            break

    log.info(
        "done — %d pages OCRed, %d option sets recovered (%d with green-detected correct answer)",
        total_pages, total_options_recovered, total_correct_tagged,
    )
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    seeds_default = str(Path(__file__).resolve().parents[2] / "seeds")
    ap.add_argument("--seeds", default=seeds_default)
    ap.add_argument("--pyq-corpus", default="~/Documents/pariksha")
    ap.add_argument("--output-dir", default=None)
    ap.add_argument("--only", default=None,
                    help="Substring match on paper filename for single-paper debug")
    ap.add_argument("--max-pages", type=int, default=None)
    args = ap.parse_args()

    seeds_root = Path(args.seeds).expanduser().resolve()
    corpus_root = Path(args.pyq_corpus).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else seeds_root / "_ocr_options"
    if not corpus_root.exists():
        log.error("corpus root missing: %s", corpus_root)
        return 2
    return run(seeds_root, corpus_root, output_dir, args.only, args.max_pages)


if __name__ == "__main__":
    sys.exit(main())
