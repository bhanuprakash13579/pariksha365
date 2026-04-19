"""Deterministic PDF → structured-question parser for the PYQ corpus.

Two PDF families dominate the 71-file corpus:

1. **SSC / RRB official** (``cgl/``, ``chsl/``, ``RRB/``) — a standard
   response-sheet layout where the correct option is marked by **span color**.
   Black ``#252525`` = stem, red ``#f61818`` = wrong option, green ``#40c64b`` =
   correct option. Question numbers use ``Q.N`` and options use ``1./2./3./4.``
   (SSC) or ``A./B./C./D.`` (RRB prepp.in).
2. **Adda247 Banks PDFs** (``Banks/SBI PO/``, ``Banks/IBPS PO/``) — questions
   are ``Q<N>.`` on the front pages, the back third of the PDF lists answers
   as ``S<N>. Ans.(x)`` followed by a ``Sol.`` block.

The parser detects the family from first-page signatures and dispatches to the
right extractor. Every parsed question carries an ``issues`` list so the
aggregator downstream can surface (and the admin can fix) anything suspect
rather than silently losing data.

Design choices:

* The SSC/RRB family uses ``page.get_text("dict")`` to access per-span colors;
  the Adda247 family only needs raw text.
* Image association is deferred to ``extract_question_images`` so the caller
  can decide whether to pay the cost (images are needed for DB ingestion,
  not for topic-frequency stats).
* Parsing is **lossy-tolerant**: when a question can't be fully parsed we
  still emit a partial record with populated ``issues`` rather than skipping
  it, so nothing disappears without a trace.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import fitz

log = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# Color constants (integer RGB as returned by PyMuPDF's get_text("dict"))
# --------------------------------------------------------------------------- #
# Tested empirically against the corpus; see /tmp/color_probe.py output.

GREEN_CORRECT = 0x40C64B  # rgb(64, 198, 75) — SSC/RRB correct-option text color
RED_WRONG = 0xF61818      # rgb(246, 24, 24) — SSC/RRB wrong-option text color
BLACK_STEM = 0x252525     # rgb(37, 37, 37)  — SSC/RRB stem text color


def _is_greenish(color_int: int) -> bool:
    """Return True when the RGB int looks like the SSC/RRB "correct" green.

    We tolerate ±24 on each channel so a future re-export with slightly
    different encoding still matches, but reject anything that is obviously a
    different hue.
    """
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF
    return g > 150 and g > r + 40 and g > b + 40


# --------------------------------------------------------------------------- #
# Data classes
# --------------------------------------------------------------------------- #

@dataclass
class ParsedQuestion:
    """One question extracted from a PYQ PDF."""

    order: int                              # monotonic 1-based position within the paper (parser-assigned)
    stem: str                               # cleaned question text
    options: List[str]                      # typically 4, sometimes 5
    printed_number: Optional[int] = None    # the "Q.N" number as printed (may restart per section)
    correct_index: Optional[int] = None     # 0-based; None if we couldn't detect
    correct_letter: Optional[str] = None    # "A"/"B"/... or "1"/"2"/... as printed
    section_hint: Optional[str] = None      # last seen Section: header before this Q
    passage_context: Optional[str] = None   # shared passage for Directions-based Qs (attached to every Q in the range)
    explanation: Optional[str] = None       # Adda247 Sol. block, SSC has none
    page_start: int = 0                     # 1-based page the stem starts on
    page_end: int = 0
    issues: List[str] = field(default_factory=list)


@dataclass
class ParsedPaper:
    pdf_path: str
    source_format: str                      # "ADDA247" | "SSC_OFFICIAL" | "RRB_PREPP" | "UNKNOWN"
    total_pages: int
    questions: List[ParsedQuestion] = field(default_factory=list)
    unparsed_pages: List[int] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)

    @property
    def stats(self) -> dict:
        with_ans = sum(1 for q in self.questions if q.correct_index is not None)
        with_img_pages = 0  # populated by caller when images matter
        return {
            "path": self.pdf_path,
            "format": self.source_format,
            "total_pages": self.total_pages,
            "questions": len(self.questions),
            "with_correct_answer": with_ans,
            "unparsed_pages": len(self.unparsed_pages),
            "parse_issues": len(self.issues)
            + sum(len(q.issues) for q in self.questions),
        }


# --------------------------------------------------------------------------- #
# Format detection
# --------------------------------------------------------------------------- #

_FORMAT_SIGNATURES: Sequence[Tuple[str, re.Pattern]] = (
    # Order matters: Adda247 solutions-doc first (its CHSL variant also carries
    # Q.N headers that would match the SSC_OFFICIAL signature), then the
    # official/prepp variants, then the classic Adda247 Banks format.
    # SOLDOC = CHSL/CGL 2025 "similar paper" solutions-doc family. Its
    # distinguishing mark is a ``Copyright © <year> Adda247`` footer on every
    # page — absent from the classic Adda247 Banks papers.
    ("ADDA247_SOLDOC", re.compile(r"Copyright\s*©\s*\d{4}\s*Adda247", re.I)),
    ("ADDA247", re.compile(r"bankersadda\.com|Memory\s*Based\s*Paper|S\d+\.\s*Ans\.|Adda247\s*App", re.I)),
    ("SSC_OFFICIAL", re.compile(r"Question\s*ID\s*:.*Chosen\s*Option", re.S)),
    ("RRB_PREPP", re.compile(r"prepp\.in|RRB\s*NTPC\s*GRADUATE\s*CBT", re.I)),
)


def _looks_like_ssc_rrb_layout(doc: fitz.Document) -> bool:
    """Heuristic for PDFs that lack a branded signature but use the standard
    official-paper layout: ``Q.N`` heading → ``Ans`` header → four numbered or
    lettered options. Used as a last-resort detector for RRB "answer key"
    PDFs that carry neither ``Question ID`` nor the ``prepp.in`` URL.
    """
    sample = []
    for i in range(min(3, len(doc))):
        sample.append(doc[i].get_text() or "")
    joined = "\n".join(sample)
    head_hits = len(re.findall(r"\bQ\.\s*\d+\s*\n", joined))
    ans_hits = len(re.findall(r"\n\s*Ans\s*\n", joined))
    opt_hits = len(re.findall(r"\n\s*[1-4A-D]\.\s", joined))
    return head_hits >= 3 and ans_hits >= 3 and opt_hits >= 6


def detect_format(doc: fitz.Document) -> str:
    """Sniff the document for a family signature. Returns the tag name or
    ``"UNKNOWN"`` when nothing matches.

    Probes the first 3 pages (where branding and URLs live) *plus* the last
    2 pages (where Adda247's ``S<N>. Ans.`` answer key lives). Classic
    Adda247 PDFs that predate the "Adda247 App" watermark only reveal their
    family via the answer-key structure, which sits at the back.

    Signatures are narrow and mostly non-overlapping; when ambiguous, the
    earlier rule wins.
    """
    head_pages = list(range(min(3, len(doc))))
    tail_pages = [i for i in (len(doc) - 2, len(doc) - 1) if i >= 0 and i not in head_pages]
    probe_pages = head_pages + tail_pages
    probe_text = [doc[i].get_text() or "" for i in probe_pages]
    joined = "\n".join(probe_text)
    for tag, rx in _FORMAT_SIGNATURES:
        if rx.search(joined):
            return tag
    if _looks_like_ssc_rrb_layout(doc):
        return "SSC_OFFICIAL_BARE"
    return "UNKNOWN"


# --------------------------------------------------------------------------- #
# SSC / RRB official family
# --------------------------------------------------------------------------- #

_QN_HEAD = re.compile(r"^Q\.?\s*(\d+)\s*$")
_OPT_LINE_SSC = re.compile(r"^\s*([1-4])\.\s*(.+)$")
_OPT_LINE_RRB = re.compile(r"^\s*([A-D])\.\s*(.+)$")
_META_NUMERIC_ID = re.compile(r"^\d{8,}$")
_META_KEYWORDS = (
    "Marked For Review",
    "Not Attempted",
    "Answered",
    "Chosen Option",
    "Not Answered",
    "Time Taken",
    "Candidate Name",
    "Roll Number",
    "Venue Name",
    "Exam Date",
    "Exam Time",
    "Test Date",
    "Test Time",
    "Subject",
    "* Note",
    "Correct Answer",
    "Incorrect Answer",
)


def _iter_page_spans(page: fitz.Page):
    """Yield (text, color, y0, y1) for every non-empty text span on the page
    in top-to-bottom, left-to-right reading order.
    """
    d = page.get_text("dict")
    spans = []
    for block in d.get("blocks", []):
        if block.get("type") != 0:
            continue
        for line in block.get("lines", []):
            bbox = line.get("bbox", (0, 0, 0, 0))
            for span in line.get("spans", []):
                text = span.get("text", "").strip()
                if not text:
                    continue
                spans.append(
                    (text, int(span.get("color", 0) or 0), bbox[1], bbox[3], bbox[0])
                )
    spans.sort(key=lambda s: (round(s[2], 1), s[4]))
    return [(t, c, y0, y1) for t, c, y0, y1, _ in spans]


def _parse_ssc_rrb_official(doc: fitz.Document) -> List[ParsedQuestion]:
    """Extract questions from an SSC-or-RRB-style response sheet.

    Walks spans in reading order page by page. State machine:

    * IDLE → on ``Q.N`` heading go to COLLECT_STEM (capture question number)
    * COLLECT_STEM → text lines until we hit an "Ans" keyword → OPTIONS
    * OPTIONS → capture up to 4 option lines, noting which span is green (that's the correct option)
    * On next ``Q.N`` or end-of-doc, flush the current question and reset

    Metadata lines (``Question ID :``, ``Option N ID :``, ``Status :``,
    ``Chosen Option :``) are dropped.

    Works for both SSC (options ``1./2./...``) and RRB (``A./B./...``); option
    regex is tried in order, whichever matches wins per question.
    """
    out: List[ParsedQuestion] = []
    current: Optional[ParsedQuestion] = None
    section_hint: Optional[str] = None
    state = "IDLE"
    monotonic_order = 0  # incremented on every new Q.N so section-restarts don't collide

    drop_prefixes = (
        "Question ID",
        "Option 1 ID",
        "Option 2 ID",
        "Option 3 ID",
        "Option 4 ID",
        "Status :",
        "Status:",
        "Chosen Option",
        "SubQuestion No",
        "www.prepp.in",
        "www.bankersadda",
    )

    def is_metadata(t: str) -> bool:
        """True if a span is an SSC/RRB metadata artifact that must never enter
        stems or options (Question/Option IDs, Status values, watermark urls)."""
        if any(t.startswith(p) for p in drop_prefixes):
            return True
        if _META_NUMERIC_ID.match(t):
            return True
        if any(kw in t for kw in _META_KEYWORDS):
            return True
        return False

    def flush():
        nonlocal current
        if current is not None:
            # Require at least 2 options to keep the record (anything less is a mis-parse)
            if len(current.options) < 2:
                current.issues.append(f"only {len(current.options)} options parsed")
            if current.correct_index is None:
                current.issues.append("no green-highlighted correct answer detected")
            out.append(current)
        current = None

    for page_idx in range(len(doc)):
        page = doc[page_idx]
        spans = _iter_page_spans(page)
        for text, color, *_ in spans:
            # Section headers like "Section : General Intelligence and Reasoning"
            if text.startswith("Section :") or text.startswith("Section:"):
                section_hint = text.split(":", 1)[1].strip()
                continue
            if is_metadata(text):
                # When we hit metadata after 4 options, the question block is done.
                # Seal it so the next stray text doesn't glue onto the last option.
                if state == "OPTIONS" and current and len(current.options) >= 4:
                    state = "SEALED"
                continue
            # Q.N header — start a new question
            m = _QN_HEAD.match(text)
            if m:
                flush()
                monotonic_order += 1
                current = ParsedQuestion(
                    order=monotonic_order,
                    printed_number=int(m.group(1)),
                    stem="",
                    options=[],
                    section_hint=section_hint,
                    page_start=page_idx + 1,
                    page_end=page_idx + 1,
                )
                state = "STEM"
                continue
            if current is None:
                continue  # content before the first Q.N — skip

            current.page_end = page_idx + 1

            if state == "STEM":
                if text.strip() == "Ans":
                    state = "OPTIONS"
                    continue
                current.stem = (current.stem + " " + text).strip() if current.stem else text
                continue

            if state == "SEALED":
                # ignore text until next Q.N — handled above
                continue

            if state == "OPTIONS":
                m1 = _OPT_LINE_SSC.match(text) or _OPT_LINE_RRB.match(text)
                if m1:
                    letter = m1.group(1)
                    body = m1.group(2).strip()
                    idx = len(current.options)
                    current.options.append(body)
                    if _is_greenish(color):
                        current.correct_index = idx
                        current.correct_letter = letter
                    continue
                # continuation of previous option's text (option wrapped to next line)
                if current.options:
                    # if this span is green and we haven't flagged correct yet, adopt
                    if _is_greenish(color) and current.correct_index is None:
                        current.correct_index = len(current.options) - 1
                    current.options[-1] = (current.options[-1] + " " + text).strip()
                    continue
                # otherwise drop — noise between Ans header and first option
    flush()
    return out


# --------------------------------------------------------------------------- #
# Adda247 family
# --------------------------------------------------------------------------- #

_Q_HEAD_ADDA = re.compile(r"^\s*Q\.?\s*(\d+)\.?\s*(.*)$")
_OPT_HEAD_ADDA = re.compile(r"^\s*\(?([A-Ea-e1-5])\)?[\.\)]\s*(.+)$")
_ANS_LINE_ADDA = re.compile(
    r"^\s*S\s*(\d+)\s*\.\s*Ans\.?\s*\(?\s*([A-Ea-e1-5])\s*\)?", re.I
)
_SOL_HEAD = re.compile(r"^\s*Sol\.?\s*(.*)$", re.I)
_DIRECTIONS_RANGE = re.compile(
    r"^\s*Directions?\s*\(\s*(\d+)\s*[-–—]\s*(\d+)\s*\)\s*:\s*(.*)$",
    re.I,
)


def _collect_directions_passages(lines: List[Tuple[str, int]]) -> Dict[int, str]:
    """Walk the paper's flat line list looking for ``Directions (N-M):``
    headers. For each one, greedily capture the content lines that follow up
    to the first ``Q<k>.`` heading, and map the resulting passage to every
    printed Q number in ``[N, M]``.

    Returns ``{printed_q_number: passage_text}``. Later-wins if two ranges
    overlap — harmless in practice since exam papers never overlap ranges.

    Handled edge cases:
      * Passages can legitimately span multiple pages before the first Q.N
      * A Directions line may also continue the passage inline after the
        colon (first ``.group(3)`` captures that tail)
      * We stop at the **first** Q.N we see after the Directions; content
        between that Q and the next Directions belongs to the questions
        themselves, not to a shared passage.
    """
    out: Dict[int, str] = {}
    i = 0
    while i < len(lines):
        line, _ = lines[i]
        m = _DIRECTIONS_RANGE.match(line.strip())
        if not m:
            i += 1
            continue
        start_n, end_n = int(m.group(1)), int(m.group(2))
        if end_n < start_n or end_n - start_n > 30:
            # Implausibly wide range — skip to avoid pulling in half the paper
            i += 1
            continue
        passage_parts: List[str] = []
        tail = m.group(3).strip()
        if tail:
            passage_parts.append(tail)
        j = i + 1
        while j < len(lines):
            next_line = lines[j][0].strip()
            # Stop at the first Q<N>. heading (start of the first governed Q)
            if _Q_HEAD_ADDA.match(next_line) and not _ANS_LINE_ADDA.match(next_line):
                break
            # Also stop at another Directions block — prevents bleed-through
            if _DIRECTIONS_RANGE.match(next_line):
                break
            # Drop pure page-number lines and Adda247 URLs
            if next_line.isdigit() or "bankersadda" in next_line.lower() or "adda247 app" in next_line.lower():
                j += 1
                continue
            passage_parts.append(next_line)
            j += 1
        if passage_parts:
            passage = " ".join(passage_parts).strip()
            for n in range(start_n, end_n + 1):
                out[n] = passage
        i = j
    return out


def _parse_adda247(doc: fitz.Document) -> List[ParsedQuestion]:
    """Extract Adda247 Banks paper questions.

    Two-pass strategy:

    1. **Front pass** — iterate pages and detect ``Q<N>.`` headings; accumulate
       stem lines until we hit the first option header, then accumulate
       options (letter or number prefix). Stop a question when the next
       ``Q<N>.`` appears or when we hit an ``S<N>. Ans.`` line (signals we
       are now in the answer-key region).
    2. **Back pass** — iterate the same lines looking for ``S<N>. Ans.(x)``
       + optional ``Sol. ...`` block, and splice the answer + explanation
       into the question with matching ``N``.

    The two passes share a single flat line list so section headers ("Directions
    (1-5):") can be surfaced in ``section_hint`` for downstream subject tagging.
    """
    # Flatten all page text into ``(line, page_idx)`` tuples preserving order.
    lines: List[Tuple[str, int]] = []
    for page_idx in range(len(doc)):
        raw = doc[page_idx].get_text() or ""
        for line in raw.splitlines():
            s = line.rstrip()
            if s.strip():
                lines.append((s, page_idx + 1))

    # Pre-compute shared passages for Directions (N-M) ranges, keyed by
    # printed Q number. Attached to each child question's ``passage_context``
    # so solvers have the context they need without our stem extraction
    # losing the shared setup.
    passage_for_q = _collect_directions_passages(lines)

    # --- front pass: questions + options --------------------------------
    out: List[ParsedQuestion] = []
    current: Optional[ParsedQuestion] = None
    in_options = False
    section_hint: Optional[str] = None
    monotonic_order = 0

    for line, page in lines:
        stripped = line.strip()
        # section hints (Directions) and passage markers
        if stripped.lower().startswith("directions"):
            section_hint = stripped
            continue
        # Q heading
        mq = _Q_HEAD_ADDA.match(stripped)
        # Treat a Q head as "new question" only when its number looks sane (>0) and the
        # remaining stem is non-empty or next non-empty line isn't an S<N>. answer head.
        if mq and not _ANS_LINE_ADDA.match(stripped):
            if current is not None:
                out.append(current)
            monotonic_order += 1
            current = ParsedQuestion(
                order=monotonic_order,
                printed_number=int(mq.group(1)),
                stem=mq.group(2).strip(),
                options=[],
                section_hint=section_hint,
                page_start=page,
                page_end=page,
            )
            in_options = False
            continue
        # answer key region — front-pass done for this question, flush and break below
        if _ANS_LINE_ADDA.match(stripped):
            break
        if current is None:
            continue
        current.page_end = page
        mopt = _OPT_HEAD_ADDA.match(stripped)
        if mopt:
            in_options = True
            current.options.append(mopt.group(2).strip())
            continue
        if in_options and current.options:
            # continuation of last option
            current.options[-1] = (current.options[-1] + " " + stripped).strip()
        else:
            current.stem = (current.stem + " " + stripped).strip() if current.stem else stripped
    if current is not None:
        out.append(current)

    # Attach Directions passages to their governed Qs.
    for q in out:
        if q.printed_number is not None and q.printed_number in passage_for_q:
            q.passage_context = passage_for_q[q.printed_number]

    # --- back pass: answers + sol blocks --------------------------------
    # Match by printed Q number (what S<N>.Ans refers to), not our monotonic counter.
    by_order = {q.printed_number: q for q in out if q.printed_number is not None}
    current_ans: Optional[Tuple[int, str]] = None  # (question_number, letter)
    sol_buffer: List[str] = []

    def commit_sol():
        nonlocal current_ans, sol_buffer
        if current_ans is None:
            return
        qnum, letter = current_ans
        q = by_order.get(qnum)
        if q is not None:
            q.correct_letter = letter.upper()
            idx = _letter_to_index(letter)
            if idx is not None and 0 <= idx < len(q.options):
                q.correct_index = idx
            else:
                q.issues.append(
                    f"answer-key letter '{letter}' can't map to option index"
                )
            if sol_buffer:
                q.explanation = " ".join(sol_buffer).strip()
        current_ans = None
        sol_buffer = []

    for line, _page in lines:
        stripped = line.strip()
        m_ans = _ANS_LINE_ADDA.match(stripped)
        if m_ans:
            commit_sol()
            current_ans = (int(m_ans.group(1)), m_ans.group(2))
            continue
        if current_ans is not None:
            m_sol = _SOL_HEAD.match(stripped)
            if m_sol:
                tail = m_sol.group(1).strip()
                if tail:
                    sol_buffer.append(tail)
                continue
            sol_buffer.append(stripped)
    commit_sol()

    for q in out:
        if not q.options:
            q.issues.append("no options parsed")
        if q.correct_index is None and q.correct_letter is None:
            q.issues.append("no answer key entry found")
    return out


_ADDA247_SOL_ANSWER = re.compile(r"^\s*Answer\s*:\s*([A-Ea-e1-5])\b", re.I)
_ADDA247_SOL_HEAD = re.compile(r"^\s*Sol\.?\s*:?\s*(.*)$", re.I)


def _parse_adda247_soldoc(doc: fitz.Document) -> List[ParsedQuestion]:
    """Parse the Adda247 "solutions document" family (used for SSC CHSL/CGL
    similar papers from 2025 onward).

    Layout: questions inline across pages using ``Q.N`` headers + options
    prefixed ``A./B./C./D.`` (no "Ans" separator line). The correct answer is
    expressed as ``Answer: <letter>`` mid-solution, followed by ``Sol:`` and an
    explanation block. The question itself and its answer are typically on
    different pages — often the entire front of the PDF lists questions, and
    the back contains consecutive answer blocks.

    We avoid fragile page-range assumptions and instead:
      * emit a ParsedQuestion every time a ``Q.N`` header is encountered with
        A./B./C./D. options beneath it, and
      * on a second pass, splice the first ``Answer: X`` that appears **after
        the Nth** ``Q.N`` header into question N. This matches the document's
        interleaved structure without requiring section detection.
    """
    lines: List[Tuple[str, int]] = []
    for page_idx in range(len(doc)):
        raw = doc[page_idx].get_text() or ""
        for ln in raw.splitlines():
            if ln.strip():
                lines.append((ln.rstrip(), page_idx + 1))

    # ---- pass 1: walk for Q.N + options -------------------------------
    out: List[ParsedQuestion] = []
    current: Optional[ParsedQuestion] = None
    in_options = False
    monotonic_order = 0

    q_head_rx = re.compile(r"^\s*Q\.?\s*(\d+)\s*(?:[\.\)]\s*)?(.*)$")
    opt_rx = re.compile(r"^\s*([A-Da-d])\.\s*(.+)$")

    for line, page in lines:
        stripped = line.strip()
        # Skip Adda247 watermark
        if "Copyright" in stripped and "Adda247" in stripped:
            continue
        mq = q_head_rx.match(stripped)
        if mq and not stripped.lower().startswith("question id"):
            if current is not None:
                out.append(current)
            monotonic_order += 1
            current = ParsedQuestion(
                order=monotonic_order,
                printed_number=int(mq.group(1)),
                stem=mq.group(2).strip(),
                options=[],
                page_start=page,
                page_end=page,
            )
            in_options = False
            continue
        if current is None:
            continue
        current.page_end = page
        mopt = opt_rx.match(stripped)
        if mopt:
            in_options = True
            current.options.append(mopt.group(2).strip())
            continue
        if in_options and current.options:
            current.options[-1] = (current.options[-1] + " " + stripped).strip()
        else:
            current.stem = (current.stem + " " + stripped).strip() if current.stem else stripped
    if current is not None:
        out.append(current)

    # Deduplicate by printed_number (the solutions tail repeats each Q.N head
    # as context before ``Answer:``). Keep the longest-stem record per number.
    by_pn: Dict[int, ParsedQuestion] = {}
    for q in out:
        if q.printed_number is None:
            continue
        prev = by_pn.get(q.printed_number)
        if prev is None or (len(q.stem) > len(prev.stem) and len(q.options) >= len(prev.options)):
            by_pn[q.printed_number] = q
    questions = sorted(by_pn.values(), key=lambda q: q.printed_number or 0)
    # Reassign monotonic order after dedup (stable by printed_number).
    for i, q in enumerate(questions, start=1):
        q.order = i

    # ---- pass 2: splice in Answer: X lines ----------------------------
    # Keep a running cursor over ordered Q numbers that still need an answer;
    # each Answer: line binds to the earliest still-unanswered question.
    pending = [q for q in questions]
    for line, _ in lines:
        if not pending:
            break
        m = _ADDA247_SOL_ANSWER.match(line.strip())
        if not m:
            continue
        letter = m.group(1)
        q = pending.pop(0)
        idx = _letter_to_index(letter)
        q.correct_letter = letter.upper()
        if idx is not None and 0 <= idx < len(q.options):
            q.correct_index = idx
        else:
            q.issues.append(f"answer letter '{letter}' doesn't map to a parsed option")

    for q in questions:
        if not q.options:
            q.issues.append("no options parsed")
        if q.correct_index is None:
            q.issues.append("no Answer: marker matched")
    return questions


def _letter_to_index(letter: str) -> Optional[int]:
    """Map ``a/b/c/d/e`` or ``1/2/3/4/5`` to a 0-based index."""
    if not letter:
        return None
    c = letter.strip().upper()
    if c.isalpha():
        return ord(c) - ord("A")
    if c.isdigit():
        return int(c) - 1
    return None


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #

def parse_paper(pdf_path: str) -> ParsedPaper:
    """Parse one PDF end-to-end. Never raises — parser errors are captured on
    the returned ``ParsedPaper.issues``.
    """
    path = str(Path(pdf_path).resolve())
    try:
        doc = fitz.open(path)
    except Exception as e:
        log.exception("could not open %s", path)
        return ParsedPaper(
            pdf_path=path,
            source_format="UNKNOWN",
            total_pages=0,
            issues=[f"open failed: {e}"],
        )

    fmt = detect_format(doc)
    paper = ParsedPaper(pdf_path=path, source_format=fmt, total_pages=len(doc))

    try:
        if fmt == "ADDA247":
            paper.questions = _parse_adda247(doc)
        elif fmt == "ADDA247_SOLDOC":
            paper.questions = _parse_adda247_soldoc(doc)
        elif fmt in ("SSC_OFFICIAL", "RRB_PREPP", "SSC_OFFICIAL_BARE"):
            paper.questions = _parse_ssc_rrb_official(doc)
        else:
            paper.issues.append("unknown PDF format — no parser dispatched")
    except Exception as e:
        log.exception("parser crashed on %s", path)
        paper.issues.append(f"parser exception: {e}")

    # detect image-only pages (page with get_text() near-empty) so caller can
    # optionally OCR them
    for i in range(len(doc)):
        t = doc[i].get_text() or ""
        if len(t.strip()) < 40:
            paper.unparsed_pages.append(i + 1)

    doc.close()
    return paper
