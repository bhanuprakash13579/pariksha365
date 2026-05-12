#!/usr/bin/env python3
"""Convert EPFO PYQ extracted text files into pariksha365 PYQ JSON seed files.

Sources:
    /home/bhanu/Documents/pariksha/UPSC/EPFO/PYQ_*.txt   (APFC papers)
    /home/bhanu/Documents/pariksha/UPSC/EPFO/EOAO_*.txt   (EO/AO papers)

Output:
    backend/seeds/pyq/upsc/epfo-apfc/recruitment-test/<paper>.json
    backend/seeds/pyq/upsc/epfo-eo-ao/recruitment-test/<paper>.json

Usage:
    python -m scripts.convert_epfo_pyqs
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Optional

_BACKEND = Path(__file__).resolve().parent.parent
_SEEDS = _BACKEND / "seeds" / "pyq"
_SRC = Path("/home/bhanu/Documents/pariksha/UPSC/EPFO")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_paper_id(title: str) -> str:
    h = hashlib.sha256(title.encode()).hexdigest()[:16]
    return f"pyq_paper_{h}"


def _make_q_id(paper_id: str, seq: int) -> str:
    return f"{paper_id}_p{seq}"


def _letter_to_index(letter: str) -> int:
    return {"A": 0, "B": 1, "C": 2, "D": 3}.get(letter.upper(), -1)


# ---------------------------------------------------------------------------
# Parser for COMPILED text (PYQ_2023_compiled_text.txt, EOAO_2023_text.txt)
# These are pdftotext outputs with Q.1) ... (a) ... (b) ... (c) ... (d) ...
# and "Hence, Option X is the correct answer." explanations
# ---------------------------------------------------------------------------

def parse_compiled_pdf(text: str) -> list[dict]:
    """Parse compiled PDF text with two-pass structure.

    These files have questions (Q.1 to Q.120) in the first half with
    (a)/(b)/(c)/(d) options, then a 'Detailed Explanation' section in
    the second half that repeats Q numbers with correct answers and
    explanations.
    """
    # --- Step 1: Split file into questions-part and explanations-part ---
    # The explanation section starts with "Detailed Explanation" header
    # (may be preceded by form-feed \f)
    split_match = re.search(r'[\n\f]\s*Detailed Explanation\s*\n\s*Part', text)
    if split_match:
        q_text = text[:split_match.start()]
        expl_text = text[split_match.start():]
    else:
        # Fallback: try to find where Q.1) appears the SECOND time
        q1_positions = [m.start() for m in re.finditer(r'\nQ[\.\s]*1[\.\)]', text)]
        if len(q1_positions) >= 2:
            q_text = text[:q1_positions[1]]
            expl_text = text[q1_positions[1]:]
        else:
            q_text = text
            expl_text = ""

    # --- Step 2: Parse questions from the first half ---
    # Handle both Q.N) format and plain N. format (EO/AO 2023 uses plain numbers)
    questions = []
    q_pattern = re.compile(
        r'Q[\.\s]*(\d+)[\.\)]\s*(.*?)(?=\nQ[\.\s]*\d+[\.\)]|\Z)',
        re.DOTALL
    )
    q_matches = list(q_pattern.finditer(q_text))

    # If we got fewer than 20 Q.N matches, try plain number format
    if len(q_matches) < 20:
        q_pattern = re.compile(
            r'\n(\d{1,3})\.\s+(.*?)(?=\n\d{1,3}\.\s|\Z)',
            re.DOTALL
        )
        q_matches = list(q_pattern.finditer(q_text))

    for m in q_matches:
        q_num = int(m.group(1))
        body = m.group(2).strip()

        # Extract options (a)/(b)/(c)/(d)
        opt_pattern = re.compile(
            r'\n\s*\(([a-dA-D])\)\s*(.*?)(?=\n\s*\([a-dA-D]\)|\nQ[\.\s]*\d+|\Z)',
            re.DOTALL
        )
        options_raw = opt_pattern.findall(body)
        if len(options_raw) < 2:
            continue

        first_opt_match = opt_pattern.search(body)
        if not first_opt_match:
            continue
        stem = body[:first_opt_match.start()].strip()
        # Clean up page markers, form-feeds
        stem = re.sub(r'\d+\s*\|\s*Page', '', stem)
        stem = re.sub(r'\f', '', stem)
        stem = re.sub(r'\n+', ' ', stem).strip()
        stem = re.sub(r'\s+', ' ', stem).strip()

        options = []
        for letter, opt_text in options_raw[:4]:
            clean = re.sub(r'\d+\s*\|\s*Page', '', opt_text)
            clean = re.sub(r'\f', '', clean)
            clean = re.sub(r'\n+', ' ', clean).strip()
            clean = re.sub(r'\s+', ' ', clean).strip()
            options.append(clean)

        if len(stem) < 5 or len(options) < 2:
            continue

        questions.append({
            "q_num": q_num,
            "stem": stem,
            "options": options,
            "correct_index": None,
            "explanation": None,
        })

    # --- Step 3: Parse explanations from the second half ---
    if expl_text:
        expl_pattern = re.compile(
            r'Q[\.\s]*(\d+)[\.\)]\s*(.*?)(?=\nQ[\.\s]*\d+[\.\)]|\Z)',
            re.DOTALL
        )
        expl_map: dict[int, dict] = {}
        for m in expl_pattern.finditer(expl_text):
            eq_num = int(m.group(1))
            ebody = m.group(2).strip()

            correct_idx = -1
            explanation = ""

            # "Hence, Option X is the correct answer"
            ans_match = re.search(
                r'Hence,?\s*Option\s+([A-Da-d])\s+is\s+(?:the\s+)?correct',
                ebody
            )
            if ans_match:
                correct_idx = _letter_to_index(ans_match.group(1))

            # "The correct option is (x)"
            if correct_idx < 0:
                ans2 = re.search(r'correct option is\s*\(?([A-Da-d])\)?', ebody)
                if ans2:
                    correct_idx = _letter_to_index(ans2.group(1))

            # Extract explanation text
            expl_body = re.sub(r'Detailed Explanation:\s*', '', ebody)
            expl_body = re.sub(r'Hence,?\s*Option\s+[A-Da-d]\s+is\s+(?:the\s+)?correct\s+answer\.?\s*', '', expl_body)
            expl_body = re.sub(r'\d+\s*\|\s*Page', '', expl_body)
            expl_body = re.sub(r'\f', '', expl_body)
            expl_body = re.sub(r'\n+', ' ', expl_body).strip()
            expl_body = re.sub(r'\s+', ' ', expl_body).strip()

            expl_map[eq_num] = {
                "correct_index": correct_idx if correct_idx >= 0 else None,
                "explanation": expl_body if expl_body else None,
            }

        # Merge explanations into questions
        for q in questions:
            qn = q["q_num"]
            if qn in expl_map:
                if expl_map[qn].get("correct_index") is not None:
                    q["correct_index"] = expl_map[qn]["correct_index"]
                if expl_map[qn].get("explanation"):
                    q["explanation"] = expl_map[qn]["explanation"]

    return questions


# ---------------------------------------------------------------------------
# Parser for RAW text (PYQ_2020_text.txt, PYQ_2025_Dec_text.txt)
# These have Q1: stem\n  (a) opt\n  (b) opt\n  [Answer: (x)]
# ---------------------------------------------------------------------------

def parse_raw_text(text: str) -> list[dict]:
    """Parse raw transcribed text with Q1: format and [Answer: (x)] markers."""
    questions = []

    # Split by Q followed by number
    q_pattern = re.compile(
        r'Q(\d+)[:\.\)]\s*(.*?)(?=\nQ\d+[:\.\)]|\n={5,}|\Z)',
        re.DOTALL
    )

    for m in q_pattern.finditer(text):
        q_num = int(m.group(1))
        body = m.group(2).strip()

        # Extract options — handle both (a) and A. formats
        opt_pattern = re.compile(
            r'\n?\s*\(?([a-dA-D])\)?[\.\)]\s*(.*?)(?=\n?\s*\(?[a-dA-D]\)?[\.\)]|\n?\s*\[Answer|\n?\s*Answer|\Z)',
            re.DOTALL
        )
        options_raw = opt_pattern.findall(body)

        if len(options_raw) < 2:
            continue

        # Stem = everything before first option
        first_opt = opt_pattern.search(body)
        if not first_opt:
            continue
        stem = body[:first_opt.start()].strip()
        # Remove trailing → or = answer markers from stem
        stem = re.sub(r'\s*[→=]\s*\w+\s*$', '', stem)
        stem = re.sub(r'\n+', ' ', stem).strip()
        stem = re.sub(r'\s+', ' ', stem).strip()

        options = []
        for letter, opt_text in options_raw[:4]:
            clean = re.sub(r'\n+', ' ', opt_text).strip()
            clean = re.sub(r'\s+', ' ', clean).strip()
            # Remove trailing answer markers
            clean = re.sub(r'\s*\[.*$', '', clean).strip()
            options.append(clean)

        # Find answer
        correct_idx = -1
        explanation = ""

        # [Answer: (x)] or [Answer: (x) — explanation]
        ans_match = re.search(r'\[Answer:\s*\(?([A-Da-d])\)?\s*(?:—\s*(.*?))?\]', body)
        if ans_match:
            correct_idx = _letter_to_index(ans_match.group(1))
            if ans_match.group(2):
                explanation = ans_match.group(2).strip()

        # Answer = (x) format
        if correct_idx < 0:
            ans2 = re.search(r'Answer\s*[:=]\s*\(?([A-Da-d])\)?', body)
            if ans2:
                correct_idx = _letter_to_index(ans2.group(1))

        # ANS: (x)
        if correct_idx < 0:
            ans3 = re.search(r'ANS:\s*\(?([A-Da-d])\)?', body)
            if ans3:
                correct_idx = _letter_to_index(ans3.group(1))

        # ← ANSWER marker on an option line
        if correct_idx < 0:
            arrow = re.search(r'\(([a-dA-D])\).*?←\s*ANSWER', body)
            if arrow:
                correct_idx = _letter_to_index(arrow.group(1))

        if len(stem) < 5 or len(options) < 2:
            continue

        questions.append({
            "q_num": q_num,
            "stem": stem,
            "options": options,
            "correct_index": correct_idx if correct_idx >= 0 else None,
            "explanation": explanation or None,
        })

    return questions


# ---------------------------------------------------------------------------
# Parser for SetB format (PYQ_SetB_2023_Jul_text.txt)
# Q1. stem\n(a) opt  (b) opt  (c) opt  (d) opt\nANS: (x)
# ---------------------------------------------------------------------------

def parse_setb_text(text: str) -> list[dict]:
    """Parse Set B format with inline ANS markers."""
    return parse_raw_text(text)  # Same logic works


# ---------------------------------------------------------------------------
# Merge answer keys from separate sources
# For papers with answer-key-only data (2002, 2004, etc.)
# ---------------------------------------------------------------------------

def parse_answer_key_line(line: str) -> dict[int, str]:
    """Parse '1C 2A 3B ...' format answer keys."""
    answers = {}
    for m in re.finditer(r'(\d+)([A-Da-d*])', line):
        q_num = int(m.group(1))
        ans = m.group(2).upper()
        if ans != '*':
            answers[q_num] = ans
    return answers


def parse_answer_keys_from_file(text: str) -> dict[int, str]:
    """Extract answer key from files that have 'ANSWER KEY:' section."""
    answers = {}
    in_key = False
    for line in text.splitlines():
        if 'ANSWER KEY' in line.upper():
            in_key = True
            continue
        if in_key and re.match(r'^\d+[A-D]', line.strip()):
            answers.update(parse_answer_key_line(line.strip()))
        elif in_key and not line.strip():
            continue
        elif in_key and not re.match(r'^\d+[A-D]', line.strip()):
            if line.strip().startswith('['):
                continue  # Skip notes like [Q66 = * (cancelled)]
            in_key = False
    return answers


# ---------------------------------------------------------------------------
# Topic classifier — maps question content to subject/topic
# ---------------------------------------------------------------------------

def classify_question(stem: str, q_num: int) -> tuple[str, str]:
    """Rough classifier for EPFO PYQ questions into subject/topic."""
    s = stem.lower()

    # English
    if q_num <= 20 or any(k in s for k in ['underlined', 'synonym', 'antonym', 'passage',
                                             'fill in the blank', 'preposition', 'phrasal',
                                             'idiom', 'vocabulary', 'rearrange', 'sentence',
                                             'grammar', 'comprehension']):
        if q_num <= 20:
            return "English", "Language & Comprehension"

    # Labour Laws / Social Security
    if any(k in s for k in ['epf', 'provident fund', 'gratuity', 'esi ', 'maternity benefit',
                             'trade union', 'industrial dispute', 'factories act', 'minimum wage',
                             'bonus act', 'workmen', 'labour', 'social security', 'pension scheme',
                             'edli', 'eps ', 'employees', 'compensation act', 'contract labour',
                             'inter-state migrant', 'child labour', 'posh', 'sexual harassment']):
        return "Labour Laws & Social Security", "Industrial Relations"

    # Accounting
    if any(k in s for k in ['trial balance', 'journal', 'ledger', 'debit', 'credit',
                             'gross profit', 'depreciation', 'accounting', 'balance sheet',
                             'conservatism', 'auditing', 'inventory valuation']):
        return "Accounting & Auditing", "Fundamentals"

    # Polity
    if any(k in s for k in ['constitution', 'article', 'parliament', 'president',
                             'supreme court', 'high court', 'fundamental rights', 'dpsp',
                             'election commission', 'schedule', 'amendment', 'writ',
                             'lok sabha', 'rajya sabha', 'governor', 'judiciary',
                             'federalism', 'upsc', 'panchayat']):
        return "Indian Polity", "Constitution & Governance"

    # Economy
    if any(k in s for k in ['gdp', 'inflation', 'fiscal', 'monetary', 'rbi ',
                             'budget', 'tax', 'niti aayog', 'five year plan',
                             'disinvestment', 'trade', 'export', 'import',
                             'poverty', 'employment', 'sez ', 'epz']):
        return "Indian Economy", "Macroeconomics"

    # History
    if any(k in s for k in ['gandhi', 'nehru', 'freedom', 'british', 'mughal',
                             'congress', 'independence', 'revolt', 'movement',
                             'civil disobedience', 'quit india', 'partition',
                             'ancient', 'medieval', 'chronological', 'vijayanagara',
                             'nalanda', 'kingdom', 'dynasty', 'cabinet mission']):
        return "History", "Modern India"

    # Science
    if any(k in s for k in ['chemical', 'element', 'compound', 'atom', 'molecule',
                             'physics', 'biology', 'vitamin', 'dna', 'chromosome',
                             'alloy', 'reaction', 'wavelength', 'electric', 'magnetic',
                             'force', 'energy', 'cell', 'tissue', 'gene']):
        return "General Science", "Science & Technology"

    # Computer
    if any(k in s for k in ['computer', 'software', 'hardware', 'ram ', 'rom ',
                             'cache', 'browser', 'internet', 'network', 'binary',
                             'algorithm', 'database', 'spreadsheet', 'usb',
                             'programming', 'operating system', 'cloud computing']):
        return "Computer Awareness", "Information Technology"

    # Mathematics
    if any(k in s for k in ['average', 'ratio', 'percentage', 'probability',
                             'triangle', 'circle', 'speed', 'distance', 'time',
                             'age', 'profit', 'loss', 'interest', 'divisible',
                             'remainder', 'sequence', 'arithmetic mean']):
        return "Mathematics", "Quantitative Aptitude"

    # Geography
    if any(k in s for k in ['river', 'mountain', 'ocean', 'climate', 'rainfall',
                             'soil', 'forest', 'national park', 'sanctuary',
                             'ramsar', 'wetland', 'state', 'capital']):
        return "Geography", "Indian Geography"

    # Default based on question number ranges (typical EPFO pattern)
    if q_num <= 20:
        return "English", "Language & Comprehension"
    elif q_num <= 40:
        return "General Studies", "Mixed"
    elif q_num <= 60:
        return "General Studies", "Science & Mathematics"
    elif q_num <= 80:
        return "General Studies", "Polity & History"
    elif q_num <= 100:
        return "General Studies", "Economy & Current Affairs"
    else:
        return "General Studies", "Labour Laws & Social Security"


# ---------------------------------------------------------------------------
# JSON builder
# ---------------------------------------------------------------------------

def build_pyq_json(
    questions: list[dict],
    title: str,
    body_slug: str,
    exam_slug: str,
    stage_slug: str,
    paper_date: Optional[str] = None,
    paper_shift: Optional[str] = None,
    total_questions: int = 120,
    source_path: Optional[str] = None,
) -> dict:
    """Build the pariksha365 PYQ JSON structure."""
    paper_id = _make_paper_id(title)

    json_questions = []
    for i, q in enumerate(questions, 1):
        subject, topic = classify_question(q["stem"], q.get("q_num", i))

        # Build options as list of strings
        opts = q["options"]
        while len(opts) < 4:
            opts.append("")  # Pad to 4 if needed

        correct_idx = q.get("correct_index")
        correct_letter = None
        if correct_idx is not None and 0 <= correct_idx < len(opts):
            correct_letter = chr(65 + correct_idx)  # A, B, C, D

        json_questions.append({
            "id": _make_q_id(paper_id, i),
            "stem": q["stem"],
            "passage_context": None,
            "options": opts[:4],
            "correct_index": correct_idx,
            "correct_letter": correct_letter,
            "explanation": q.get("explanation"),
            "subject": subject,
            "topic": topic,
            "difficulty": "MEDIUM",
            "images": [],
            "source": {
                "printed_number": str(q.get("q_num", i)),
                "page": None,
            },
        })

    return {
        "schema_version": 1,
        "id": paper_id,
        "title": title,
        "description": f"UPSC EPFO Previous Year Questions — {title}",
        "test_type": "PYQ",
        "body_slug": body_slug,
        "exam_slug": exam_slug,
        "stage_slug": stage_slug,
        "total_duration_minutes": 120,
        "total_questions": total_questions,
        "negative_marking": 0.8333,
        "has_sectional_timing": False,
        "source_pdf_path": source_path,
        "source_format": "UPSC_EPFO_EXTRACTED",
        "paper_date": paper_date,
        "paper_shift": paper_shift,
        "sanctioned_override": len(json_questions),
        "parse_health": {
            "total_questions": len(json_questions),
            "questions_with_answer": sum(1 for q in json_questions if q["correct_index"] is not None),
            "questions_without_answer": sum(1 for q in json_questions if q["correct_index"] is None),
        },
        "sections": [
            {
                "name": "General Studies & Social Security",
                "time_limit_minutes": 120,
                "marks_per_question": 2.5,
                "order": 1,
                "questions": json_questions,
            }
        ],
    }


# ---------------------------------------------------------------------------
# Paper definitions
# ---------------------------------------------------------------------------

PAPERS = [
    # APFC 2020
    {
        "src": "PYQ_2020_text.txt",
        "parser": "raw",
        "title": "UPSC EPFO APFC 2020 (Conducted 2021)",
        "exam_slug": "epfo-apfc",
        "stage_slug": "recruitment-test",
        "output_dir": "upsc/epfo-apfc/recruitment-test",
        "output_name": "EPFO-APFC-PYQ-2020.json",
        "paper_date": "2021-01-01",
        "total_questions": 120,
    },
    # APFC 2023 (Set A — compiled with explanations)
    {
        "src": "PYQ_2023_compiled_text.txt",
        "parser": "compiled",
        "title": "UPSC EPFO APFC 2023 (Set A)",
        "exam_slug": "epfo-apfc",
        "stage_slug": "recruitment-test",
        "output_dir": "upsc/epfo-apfc/recruitment-test",
        "output_name": "EPFO-APFC-PYQ-2023-Set-A.json",
        "paper_date": "2023-07-03",
        "total_questions": 120,
    },
    # APFC 2023 (Set B)
    {
        "src": "PYQ_SetB_2023_Jul_text.txt",
        "parser": "raw",
        "title": "UPSC EPFO APFC 2023 (Set B)",
        "exam_slug": "epfo-apfc",
        "stage_slug": "recruitment-test",
        "output_dir": "upsc/epfo-apfc/recruitment-test",
        "output_name": "EPFO-APFC-PYQ-2023-Set-B.json",
        "paper_date": "2023-07-02",
        "paper_shift": "Set B",
        "total_questions": 120,
    },
    # APFC + EO/AO 2025 (combined paper — under APFC)
    {
        "src": "PYQ_2025_Dec_text.txt",
        "parser": "raw",
        "title": "UPSC EPFO APFC & EO/AO 2025",
        "exam_slug": "epfo-apfc",
        "stage_slug": "recruitment-test",
        "output_dir": "upsc/epfo-apfc/recruitment-test",
        "output_name": "EPFO-APFC-EO-AO-PYQ-2025.json",
        "paper_date": "2025-12-01",
        "total_questions": 120,
        "explanations_src": "PYQ_2025_compiled_text.txt",
    },
    # EO/AO 2023 (compiled with explanations)
    {
        "src": "EOAO_2023_text.txt",
        "parser": "compiled",
        "title": "UPSC EPFO EO/AO 2023",
        "exam_slug": "epfo-eo-ao",
        "stage_slug": "recruitment-test",
        "output_dir": "upsc/epfo-eo-ao/recruitment-test",
        "output_name": "EPFO-EO-AO-PYQ-2023.json",
        "paper_date": "2023-07-03",
        "total_questions": 120,
    },
    # 2025 shared under EO/AO too
    {
        "src": "PYQ_2025_Dec_text.txt",
        "parser": "raw",
        "title": "UPSC EPFO APFC & EO/AO 2025",
        "exam_slug": "epfo-eo-ao",
        "stage_slug": "recruitment-test",
        "output_dir": "upsc/epfo-eo-ao/recruitment-test",
        "output_name": "EPFO-APFC-EO-AO-PYQ-2025.json",
        "paper_date": "2025-12-01",
        "total_questions": 120,
        "explanations_src": "PYQ_2025_compiled_text.txt",
    },
]


# ---------------------------------------------------------------------------
# Explanation merger
# ---------------------------------------------------------------------------

def merge_explanations(questions: list[dict], expl_src_path: Path) -> list[dict]:
    """Merge explanations from compiled PDF into raw-parsed questions."""
    if not expl_src_path.exists():
        return questions

    expl_text = expl_src_path.read_text()
    expl_qs = parse_compiled_pdf(expl_text)
    expl_map = {}
    for eq in expl_qs:
        expl_map[eq["q_num"]] = {
            "explanation": eq.get("explanation"),
            "correct_index": eq.get("correct_index"),
        }

    for q in questions:
        qn = q.get("q_num")
        if qn in expl_map:
            if not q.get("explanation") and expl_map[qn].get("explanation"):
                q["explanation"] = expl_map[qn]["explanation"]
            if q.get("correct_index") is None and expl_map[qn].get("correct_index") is not None:
                q["correct_index"] = expl_map[qn]["correct_index"]

    return questions


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 70)
    print("EPFO PYQ Converter — pariksha365 JSON generator")
    print("=" * 70)

    results = []
    for paper in PAPERS:
        src_path = _SRC / paper["src"]
        if not src_path.exists():
            print(f"  ⚠ SKIP: {paper['src']} not found")
            continue

        text = src_path.read_text()
        print(f"\n{'─' * 60}")
        print(f"  Processing: {paper['src']}")
        print(f"  Title: {paper['title']}")

        # Parse
        if paper["parser"] == "compiled":
            questions = parse_compiled_pdf(text)
        elif paper["parser"] == "raw":
            questions = parse_raw_text(text)
        elif paper["parser"] == "setb":
            questions = parse_setb_text(text)
        else:
            print(f"  ⚠ Unknown parser: {paper['parser']}")
            continue

        print(f"  Parsed: {len(questions)} questions")

        # Merge explanations if available
        if paper.get("explanations_src"):
            expl_path = _SRC / paper["explanations_src"]
            questions = merge_explanations(questions, expl_path)
            print(f"  Merged explanations from: {paper['explanations_src']}")

        # Sort by question number
        questions.sort(key=lambda q: q.get("q_num", 0))

        # Stats
        with_answer = sum(1 for q in questions if q.get("correct_index") is not None)
        without_answer = len(questions) - with_answer
        print(f"  With answers: {with_answer}/{len(questions)}")
        if without_answer > 0:
            missing = [q["q_num"] for q in questions if q.get("correct_index") is None]
            print(f"  Missing answers for Q: {missing[:20]}{'...' if len(missing) > 20 else ''}")

        # Build JSON
        pyq_json = build_pyq_json(
            questions=questions,
            title=paper["title"],
            body_slug="upsc",
            exam_slug=paper["exam_slug"],
            stage_slug=paper["stage_slug"],
            paper_date=paper.get("paper_date"),
            paper_shift=paper.get("paper_shift"),
            total_questions=paper.get("total_questions", 120),
            source_path=paper["src"],
        )

        # Write
        out_dir = _SEEDS / paper["output_dir"]
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / paper["output_name"]
        out_path.write_text(json.dumps(pyq_json, indent=2, ensure_ascii=False))
        print(f"  ✓ Written: {out_path.relative_to(_BACKEND)}")

        results.append({
            "file": paper["output_name"],
            "questions": len(questions),
            "with_answer": with_answer,
            "without_answer": without_answer,
        })

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    print(f"{'=' * 70}")
    total_q = 0
    for r in results:
        status = "✓" if r["without_answer"] == 0 else f"⚠ {r['without_answer']} missing answers"
        print(f"  {r['file']}: {r['questions']} Qs — {status}")
        total_q += r["questions"]
    print(f"\nTotal: {total_q} questions across {len(results)} papers")

    return 0


if __name__ == "__main__":
    sys.exit(main())
