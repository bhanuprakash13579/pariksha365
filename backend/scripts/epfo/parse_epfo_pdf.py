#!/usr/bin/env python3
"""Parse EPFO APFC MCQ Bank PDF -> structured JSON.

Input:  /tmp/epfo_raw.txt   (from `pdftotext -raw …`)
Output: /tmp/epfo_questions.json  (list of {id,section,stem,options,correct_letter,explanation})
"""
import json
import re
from pathlib import Path

TXT = Path("/tmp/epfo_raw.txt")
OUT = Path("/tmp/epfo_questions.json")

HEADER_RE = re.compile(r"^EPFO APFC MCQ Question Bank .* April 2026$")
PART_HEADER_RE = re.compile(r"^(PART|Part) [IVXLC]+\b")
SECTION_MARK_RE = re.compile(r"^■ ")
Q_RE = re.compile(r"^Q(\d+)\.\s*(.*)$")
OPT_ANY_RE = re.compile(r"\(([ABCD])\)")

# Options can appear as:
#   "(A) ...  (B) ..."     — both on same line
#   "(A) ..."               — split over own line, next line may be (B)/(C)/(D) or a continuation
#   Sometimes (A) wraps onto the next line before (B) appears.
# The parser walks question body lines and segments by "(X)" markers in reading order.

ANS_LINE_RE = re.compile(r"^Q(\d+)\s+([ABCD])\b\s*(.*)$")
ANS_KEY_START = "Answer Key & Explanations"


def split_questions_section(lines):
    """Return lines between start-of-questions and Answer Key section."""
    start_idx = None
    for i, ln in enumerate(lines):
        if ln.startswith("Q1.") and start_idx is None:
            start_idx = i
            break
    end_idx = None
    for i, ln in enumerate(lines):
        if ln.strip() == ANS_KEY_START:
            end_idx = i
            break
    assert start_idx is not None and end_idx is not None, "Could not locate question bounds"
    return lines[start_idx:end_idx], lines[end_idx:]


def is_skip_line(ln: str) -> bool:
    if not ln.strip():
        return True
    if HEADER_RE.match(ln.strip()):
        return True
    if PART_HEADER_RE.match(ln.strip()):
        return True
    if SECTION_MARK_RE.match(ln.strip()):
        return True
    return False


def parse_questions(q_lines):
    """Walk the question section and split into raw question blocks keyed by Q#."""
    blocks = {}  # qnum -> list[str]
    current_num = None
    current_section = None
    for ln in q_lines:
        if is_skip_line(ln):
            continue
        if re.match(r"^Part\s+[A-Z]+\s*$", ln.strip()):
            continue
        if re.match(r"^[A-Z][a-z].*· [a-z]", ln.strip()):  # sub-header like "Post-profile · pattern · syllabus"
            continue
        m = Q_RE.match(ln.strip())
        if m:
            current_num = int(m.group(1))
            current_section = m.group(2).strip()
            blocks[current_num] = {"section": current_section, "lines": []}
            continue
        if current_num is None:
            continue
        blocks[current_num]["lines"].append(ln.rstrip())
    return blocks


def segment_options(body_lines):
    """Given accumulated body lines AFTER the Q header and section label, return (stem_text, {A,B,C,D}).

    Some PDFs put both options on same line: "(A) foo (B) bar". Others split: "(A) foo\n(B) bar".
    Option text can wrap onto the next line (without a marker).
    """
    full = "\n".join(body_lines)
    # Find first "(A)" — everything before is stem
    first_a = full.find("(A)")
    if first_a < 0:
        return full.strip(), {}
    stem = full[:first_a].strip()
    rest = full[first_a:]

    # Find option marker positions for (A) (B) (C) (D) — take the FIRST occurrence of each,
    # because option text may itself contain parenthetical letters.
    positions = {}
    for letter in "ABCD":
        idx = rest.find(f"({letter})")
        if idx >= 0:
            positions[letter] = idx

    # Sort by position
    ordered = sorted(positions.items(), key=lambda kv: kv[1])
    options = {}
    for i, (letter, pos) in enumerate(ordered):
        next_pos = ordered[i + 1][1] if i + 1 < len(ordered) else len(rest)
        segment = rest[pos:next_pos]
        # Strip "(X)" marker
        segment = segment[len(f"({letter})"):]
        # Collapse newlines into spaces
        text = re.sub(r"\s+", " ", segment).strip()
        options[letter] = text
    return stem, options


def parse_answer_key(a_lines):
    """Each answer row looks like:
         Q42 B
         explanation-line-1
         explanation-line-2
       OR
         Q42 B explanation-on-same-line ...
       Continuations end when the next "Q<num> <letter>" pattern begins.
    """
    answers = {}
    current_q = None
    current_ans = None
    explanation_buf = []
    for ln in a_lines:
        s = ln.strip()
        if not s:
            if current_q is not None and explanation_buf:
                pass  # tolerate blank lines within explanation
            continue
        if HEADER_RE.match(s):
            continue
        if s.startswith("# Ans Explanation"):
            continue
        m = ANS_LINE_RE.match(s)
        if m:
            # flush previous
            if current_q is not None:
                answers[current_q] = {
                    "letter": current_ans,
                    "explanation": re.sub(r"\s+", " ", " ".join(explanation_buf)).strip(),
                }
            current_q = int(m.group(1))
            current_ans = m.group(2)
            tail = m.group(3).strip()
            explanation_buf = [tail] if tail else []
            continue
        if current_q is not None:
            explanation_buf.append(s)
    if current_q is not None:
        answers[current_q] = {
            "letter": current_ans,
            "explanation": re.sub(r"\s+", " ", " ".join(explanation_buf)).strip(),
        }
    return answers


def main():
    lines = TXT.read_text(encoding="utf-8").splitlines()
    q_section, a_section = split_questions_section(lines)
    q_blocks = parse_questions(q_section)
    a_map = parse_answer_key(a_section)

    questions = []
    missing_opts = 0
    missing_ans = 0
    for qnum in sorted(q_blocks):
        blk = q_blocks[qnum]
        stem, opts = segment_options(blk["lines"])
        if not opts or len(opts) < 4:
            missing_opts += 1
            print(f"!! Q{qnum}: only {len(opts)} option(s) parsed. raw:")
            print("   " + "\n   ".join(blk["lines"][:6]))
            continue
        ans = a_map.get(qnum)
        if not ans:
            missing_ans += 1
            print(f"!! Q{qnum}: no answer in key")
            continue
        questions.append({
            "qnum": qnum,
            "section": blk["section"],
            "stem": re.sub(r"\s+", " ", stem).strip(),
            "options": {k: opts[k] for k in "ABCD"},
            "correct_letter": ans["letter"],
            "explanation": ans["explanation"],
        })

    OUT.write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Parsed {len(questions)} complete questions.")
    print(f"  Incomplete options: {missing_opts}")
    print(f"  Missing answers:   {missing_ans}")
    print(f"  Total answer-key entries: {len(a_map)}")
    print(f"  Total question blocks:    {len(q_blocks)}")


if __name__ == "__main__":
    main()
