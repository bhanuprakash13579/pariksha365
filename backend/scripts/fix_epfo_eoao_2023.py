#!/usr/bin/env python3
"""
Fix EPFO-EO-AO-PYQ-2023.json
- Remove 6 fake questions
- Remove duplicate Q2-Q5 entries (keep only one each)
- Add 27 missing questions from EOAO_2023_text.txt
- Fix subject/topic classifications
"""

import json, re, hashlib
from pathlib import Path

JSON_PATH = (
    "/home/bhanu/Desktop/pariksha365/backend/seeds/pyq/upsc/epfo-eo-ao"
    "/recruitment-test/EPFO-EO-AO-PYQ-2023.json"
)
SRC_TEXT = "/home/bhanu/Documents/pariksha/UPSC/EPFO/EOAO_2023_text.txt"

# ── Official answer key (A=0, B=1, C=2, D=3, -1=disputed) ────────────────────
ANS = {
     1:2,  2:3,  3:0,  4:0,  5:2,  6:3,  7:0,  8:0,  9:2, 10:1,
    11:1, 12:3, 13:2, 14:0, 15:1, 16:2, 17:0, 18:2, 19:0, 20:0,
    21:0, 22:2, 23:0, 24:1, 25:3, 26:1, 27:2, 28:3, 29:2, 30:1,
    31:3, 32:0, 33:2, 34:3, 35:2, 36:1, 37:3, 38:2, 39:0, 40:3,
    41:0, 42:2, 43:0, 44:3, 45:1, 46:0, 47:2, 48:2, 49:2, 50:2,
    51:2, 52:3, 53:0, 54:3, 55:0, 56:3, 57:1, 58:0, 59:1, 60:0,
    61:2, 62:1, 63:2, 64:3, 65:1, 66:1, 67:1, 68:2, 69:2, 70:0,
    71:0, 72:1, 73:1, 74:0, 75:2, 76:0, 77:3, 78:1, 79:0, 80:1,
    81:3, 82:2, 83:0, 84:3, 85:1, 86:3, 87:1, 88:0, 89:3, 90:0,
    91:3, 92:2, 93:3, 94:1, 95:2, 96:2, 97:3, 98:0, 99:1, 100:2,
   101:3, 102:3, 103:3, 104:1, 105:2, 106:3, 107:0, 108:1, 109:0, 110:3,
   111:0, 112:2, 113:1, 114:1, 115:2, 116:2, 117:0, 118:3, 119:1, 120:0,
}
LETTER = {0:"A", 1:"B", 2:"C", 3:"D"}

# ── Parse source text → {qnum: (stem, [options])} ─────────────────────────────
def parse_source(path):
    text = Path(path).read_text(encoding="utf-8", errors="ignore")
    lines = text.split("\n")

    # Only process Part 1 (before "UPSC EPFO EO/AO 2023 – Answers")
    cutoff = len(lines)
    for i, line in enumerate(lines):
        if "UPSC EPFO EO/AO 2023" in line and "Answers" in line:
            cutoff = i
            break
    lines = lines[:cutoff]
    # Strip form-feed (page-break) characters that appear at start of new PDF pages
    lines = [ln.lstrip('\x0c') for ln in lines]

    questions = {}
    i = 0
    while i < len(lines):
        m = re.match(r'^(\d{1,3})\.\s+(.+)', lines[i])
        if m:
            qnum = int(m.group(1))
            if 1 <= qnum <= 120:
                stem_parts = [m.group(2).strip()]
                j = i + 1
                opts = {"a": None, "b": None, "c": None, "d": None}
                # Collect stem lines until we find options
                while j < len(lines) and j < i + 60:
                    ln = lines[j].strip()
                    om = re.match(r'^\(([abcd])\)\s*(.*)', ln, re.IGNORECASE)
                    if om:
                        opt_key = om.group(1).lower()
                        opt_val = om.group(2).strip()
                        # Collect continuation of option text
                        k = j + 1
                        while k < len(lines) and k < j + 5:
                            nxt = lines[k].strip()
                            if re.match(r'^\(([abcd])\)', nxt, re.IGNORECASE):
                                break
                            if re.match(r'^\d{1,3}\.', nxt):
                                break
                            if nxt and not re.match(r'^\d+\s*\|\s*Page', nxt):
                                opt_val += " " + nxt
                            k += 1
                        opts[opt_key] = opt_val.strip()
                        j = k
                    elif ln and not re.match(r'^\d+\s*\|\s*Page', ln):
                        if not any(opts[k2] is not None for k2 in "abcd"):
                            stem_parts.append(ln)
                        j += 1
                    else:
                        j += 1
                    # Stop if we have all 4 options
                    if all(opts[k2] is not None for k2 in "abcd"):
                        break

                stem = " ".join(stem_parts).strip()
                options = [opts[k2] or "" for k2 in ["a", "b", "c", "d"]]
                if stem and options[0]:
                    questions[qnum] = (stem, options)
        i += 1
    return questions

print("Parsing source text …")
parsed = parse_source(SRC_TEXT)
print(f"  Parsed {len(parsed)} questions from source text")

# ── Load JSON ─────────────────────────────────────────────────────────────────
with open(JSON_PATH) as f:
    data = json.load(f)

qs = data["sections"][0]["questions"]
paper_id = data["id"]

# ── Remove fakes and keep only valid questions ─────────────────────────────────
def get_pn(q):
    src = q.get("source", {})
    if not isinstance(src, dict):
        return None
    pn = src.get("printed_number", "")
    if pn == "patched_from_source_text" or not str(pn).isdigit():
        return None
    return int(pn)

# Keep one entry per printed_number (remove dupes — keep first occurrence)
seen = set()
real_qs = []
removed = 0
for q in qs:
    pn = get_pn(q)
    if pn is None:
        removed += 1
        continue
    if pn in seen:
        removed += 1
        continue
    seen.add(pn)
    real_qs.append(q)

print(f"Removed {removed} fake/duplicate questions; kept {len(real_qs)}")

# ── Classification map ────────────────────────────────────────────────────────
SUBJ = {
    # English Part A Q1-Q20
    **{n: ("English", "Fill in the Blanks", "ENG_GRAMMAR") for n in range(1, 6)},
    **{n: ("English", "Reading Comprehension", "ENG_RC") for n in range(6, 11)},
    **{n: ("English", "Sentence Arrangement", "ENG_GRAMMAR") for n in range(11, 16)},
    **{n: ("English", "Error Detection", "ENG_GRAMMAR") for n in range(16, 21)},
    # History Q21-Q24
    21: ("History", "Modern India", "HIS_MODERN"),
    22: ("History", "Modern India", "HIS_MODERN"),
    23: ("History", "Modern India", "HIS_MODERN"),
    24: ("History", "Modern India", "HIS_MODERN"),
    25: ("History", "Modern India", "HIS_MODERN"),
    # Labour Laws Q26-Q30
    26: ("Labour Laws & Social Security", "Industrial Employment", "EPFO_IR"),
    27: ("Labour Laws & Social Security", "Labour Legislation", "EPFO_IR"),
    28: ("Labour Laws & Social Security", "Contract Labour Act", "EPFO_IR"),
    29: ("Labour Laws & Social Security", "Industrial Disputes Act", "EPFO_IR"),
    30: ("Labour Laws & Social Security", "Factories Act", "EPFO_FACTORIES"),
    # Mathematics Q31-Q35, Q41-Q45, Q96
    **{n: ("Mathematics", "Arithmetic", "MATH_QA") for n in [31,32,33,34,35,41,42,43,44,45,96]},
    # Accounting Q36-Q40, Q61-Q65
    **{n: ("Accounting & Auditing", "Financial Accounting", "ACCT_PRINCIPLES")
       for n in [36,37,38,39,40,61,62,63,64,65]},
    # GS/Current Affairs Q46-Q60
    46: ("General Studies", "Social Policy", "GS_MISC"),
    47: ("General Studies", "Geography", "GS_MISC"),
    48: ("General Studies", "Economy", "GS_MISC"),
    49: ("General Studies", "Government Schemes", "GS_MISC"),
    50: ("General Studies", "Government Schemes", "GS_MISC"),
    51: ("Indian Economy", "Monetary Policy", "ECO_MISC"),
    52: ("Indian Economy", "Banking & Finance", "ECO_MISC"),
    53: ("Indian Economy", "Banking & Finance", "ECO_MISC"),
    54: ("General Studies", "Economy", "GS_MISC"),
    55: ("General Studies", "Economy", "GS_MISC"),
    56: ("General Studies", "Science & Technology", "GS_MISC"),
    57: ("General Studies", "Environment", "GS_ENV"),
    58: ("Indian Economy", "Taxation", "ECO_MISC"),
    59: ("General Studies", "Science & Technology", "GS_MISC"),
    60: ("General Studies", "Economy", "GS_MISC"),
    # Computer Awareness Q66-Q70, Q101-Q105
    **{n: ("Computer Awareness", "Computer Fundamentals", "COMP_FUND")
       for n in [66,67,68,69,70,101,102,103,104,105]},
    # Science Q71-Q75, Q106-Q110
    71: ("General Science", "Biology", "SCI_BIOLOGY"),
    72: ("General Science", "Biology", "SCI_BIOLOGY"),
    73: ("General Science", "Chemistry", "SCI_CHEMISTRY"),
    74: ("General Science", "Chemistry", "SCI_CHEMISTRY"),
    75: ("General Science", "Physics", "SCI_PHYSICS"),
    106: ("General Science", "Physics", "SCI_PHYSICS"),
    107: ("General Science", "Physics", "SCI_PHYSICS"),
    108: ("General Science", "Chemistry", "SCI_CHEMISTRY"),
    109: ("General Science", "Chemistry", "SCI_CHEMISTRY"),
    110: ("General Science", "Chemistry", "SCI_CHEMISTRY"),
    # Polity Q76-Q82, Q111
    **{n: ("Indian Polity", "Constitutional Provisions", "POL_CONSTITUTION")
       for n in [76,77,78,79,80,81,82,111]},
    # History Q83-Q85
    83: ("History", "Modern India", "HIS_MODERN"),
    84: ("History", "Modern India", "HIS_MODERN"),
    85: ("History", "Modern India", "HIS_MODERN"),
    # Labour Laws Q86-Q95, Q112-Q120
    **{n: ("Labour Laws & Social Security", "Labour Legislation", "EPFO_IR")
       for n in [86,87,88,89,90,91,92,93,94,95,116,117,118,119,120]},
    # Reasoning Q97-Q100
    **{n: ("Reasoning", "Logical Reasoning", "REAS_ARRANGEMENT")
       for n in [97,98,99,100]},
    # GS / Polity Q112-Q115
    112: ("General Studies", "Environment", "GS_ENV"),
    113: ("Indian Polity", "Constitutional Provisions", "POL_CONSTITUTION"),
    114: ("Indian Economy", "Budget & Finance", "ECO_MISC"),
    115: ("General Studies", "Science & Technology", "GS_MISC"),
}

# ── Build missing question entries from parsed source ─────────────────────────
existing_nums = {get_pn(q) for q in real_qs}
missing = [n for n in range(1, 121) if n not in existing_nums]
print(f"Missing Q numbers: {missing}")

def make_id(paper_id, num):
    h = hashlib.md5(f"{paper_id}_q{num:03d}".encode()).hexdigest()[:8]
    return f"{paper_id}_q{num:03d}_{h}"

added = 0
for qnum in missing:
    if qnum not in parsed:
        print(f"  WARNING: Q{qnum} not found in source text — skipping")
        continue

    stem, options = parsed[qnum]
    ci = ANS.get(qnum, 0)
    cl = LETTER.get(ci, "A") if ci >= 0 else "A"
    correct_option = options[ci] if ci >= 0 and ci < len(options) else ""

    subj_info = SUBJ.get(qnum, ("General Studies", "General Knowledge", "GS_MISC"))
    subj, topic, code = subj_info

    q_entry = {
        "id": make_id(paper_id, qnum),
        "stem": stem,
        "passage_context": None,
        "options": options,
        "correct_index": ci if ci >= 0 else 3,
        "correct_letter": cl,
        "explanation": (
            f"The correct answer is ({cl}) {correct_option}. "
            f"{'[Answer disputed in official key]' if ci < 0 else ''}"
        ),
        "subject": subj,
        "topic": topic,
        "topic_code": code,
        "difficulty": "MEDIUM",
        "images": [],
        "source": {"printed_number": str(qnum), "page": None},
    }
    real_qs.append(q_entry)
    added += 1

print(f"Added {added} missing questions")

# ── Apply classification fixes to existing questions ──────────────────────────
for q in real_qs:
    pn = get_pn(q)
    if pn and pn in SUBJ:
        subj, topic, code = SUBJ[pn]
        q["subject"] = subj
        q["topic"] = topic
        q["topic_code"] = code
    # Correct the answer if current JSON has wrong correct_index
    if pn and pn in ANS and ANS[pn] >= 0:
        official_ci = ANS[pn]
        if q["correct_index"] != official_ci:
            q["correct_index"] = official_ci
            q["correct_letter"] = LETTER[official_ci]

# ── Sort, verify, save ────────────────────────────────────────────────────────
real_qs.sort(key=lambda q: int(get_pn(q)))
nums = [get_pn(q) for q in real_qs]
still_missing = [n for n in range(1, 121) if n not in nums]
dupes = [n for n in set(nums) if nums.count(n) > 1]
print(f"Total: {len(real_qs)}  Missing: {still_missing}  Dupes: {dupes}")

data["sections"][0]["questions"] = real_qs
data["parse_health"]["total_questions"] = len(real_qs)
data["parse_health"]["questions_with_answer"] = len(real_qs)
data["parse_health"]["questions_without_answer"] = 0

with open(JSON_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved:", JSON_PATH)
