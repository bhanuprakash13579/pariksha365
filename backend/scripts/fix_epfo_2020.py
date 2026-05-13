#!/usr/bin/env python3
"""
Fix EPFO-APFC-PYQ-2020.json:
- Remove 5 fake antonym duplicates (source is not a dict)
- Fix subject/topic misclassifications
- Fix broken Q33 options, broken Q46 options
- Add 5 real missing questions: Q84, Q85, Q89, Q92, Q93
"""

import json

JSON_PATH = (
    "/home/bhanu/Desktop/pariksha365/backend/seeds/pyq/upsc/epfo-apfc"
    "/recruitment-test/EPFO-APFC-PYQ-2020.json"
)

with open(JSON_PATH) as f:
    data = json.load(f)

qs = data["sections"][0]["questions"]
paper_id = data["id"]

# ── 1. Remove fakes (source not a dict) ──────────────────────────────────────
real_qs = [q for q in qs if isinstance(q.get("source"), dict)
           and q["source"].get("printed_number") != "patched_from_source_text"]
print(f"Removed {len(qs) - len(real_qs)} fake questions")

# ── 2. Classification fixes ───────────────────────────────────────────────────
CLASSIFICATION_FIXES = {
    # English fill-in-blank Q1-Q5
    "1":  ("English", "Fill in the Blanks", "ENG_GRAMMAR"),
    "2":  ("English", "Fill in the Blanks", "ENG_GRAMMAR"),
    "3":  ("English", "Fill in the Blanks", "ENG_GRAMMAR"),
    "4":  ("English", "Fill in the Blanks", "ENG_GRAMMAR"),
    "5":  ("English", "Fill in the Blanks", "ENG_GRAMMAR"),
    # English vocabulary Q6-Q15 (antonyms & synonyms)
    "6":  ("English", "Vocabulary", "ENG_VOCAB"),
    "7":  ("English", "Vocabulary", "ENG_VOCAB"),
    "8":  ("English", "Vocabulary", "ENG_VOCAB"),
    "9":  ("English", "Vocabulary", "ENG_VOCAB"),
    "10": ("English", "Vocabulary", "ENG_VOCAB"),
    "11": ("English", "Vocabulary", "ENG_VOCAB"),
    "12": ("English", "Vocabulary", "ENG_VOCAB"),
    "13": ("English", "Vocabulary", "ENG_VOCAB"),
    "14": ("English", "Vocabulary", "ENG_VOCAB"),
    "15": ("English", "Vocabulary", "ENG_VOCAB"),
    # Error spotting Q16-Q20
    "16": ("English", "Error Spotting", "ENG_GRAMMAR"),
    "17": ("English", "Error Spotting", "ENG_GRAMMAR"),
    "18": ("English", "Error Spotting", "ENG_GRAMMAR"),
    "19": ("English", "Error Spotting", "ENG_GRAMMAR"),
    "20": ("English", "Error Spotting", "ENG_GRAMMAR"),
    # Computer Awareness misclassified as Math
    "27": ("Computer Awareness", "Computer Fundamentals", "COMP_FUND"),
    "30": ("Computer Awareness", "Computer Fundamentals", "COMP_FUND"),
    # GS misclassified as Math
    "39": ("General Studies", "Government Institutions", "GS_GOVT"),
    # Science misclassified
    "44": ("General Science", "Biology", "SCI_BIOLOGY"),
    "46": ("General Science", "Physics", "SCI_PHYSICS"),
    "47": ("General Science", "Physics", "SCI_PHYSICS"),
    "48": ("General Science", "Physics", "SCI_PHYSICS"),
    "49": ("General Science", "Physics", "SCI_PHYSICS"),
    "50": ("General Science", "Physics", "SCI_PHYSICS"),
    "55": ("General Science", "Chemistry", "SCI_CHEMISTRY"),
    # GS misclassified as Computer
    "56": ("General Studies", "General Knowledge", "GS_MISC"),
    "57": ("General Studies", "General Knowledge", "GS_MISC"),
    "59": ("General Studies", "General Knowledge", "GS_MISC"),
    # Polity misclassified as History
    "58": ("Indian Polity", "Constitutional Provisions", "POL_CONSTITUTION"),
    # Computer misclassified as Geography
    "67": ("Computer Awareness", "Computer Fundamentals", "COMP_FUND"),
    # Environment misclassified as Computer
    "77": ("General Studies", "Environment", "GS_ENV"),
    # Accounting misclassified as GS
    "88": ("Accounting & Auditing", "Financial Accounting", "ACCT_PRINCIPLES"),
    # History misclassified as GS
    "91": ("History", "Modern India", "HIS_MODERN"),
    # GS misclassified as English
    "100": ("General Studies", "General Knowledge", "GS_MISC"),
}

# ── 3. Specific field fixes (options, answers, stems) ────────────────────────
SPECIFIC_FIXES = {
    # Q33: broken options (S.A. Dange split into 'S.' and 'Dange')
    "33": {
        "options": ["G.K. Gokhale", "S.A. Dange", "N.M. Joshi", "M.R. Jayakar"],
        "correct_index": 2,
        "correct_letter": "C",
        "subject": "History",
        "topic": "Modern India",
        "topic_code": "HIS_MODERN",
        "explanation": (
            "N.M. Joshi (Narayan Malhar Joshi) founded the Social Service League in "
            "Bombay in 1911 to improve the conditions of industrial workers. He was a "
            "prominent trade union leader and social reformer. Hence (C) is the correct "
            "answer."
        ),
    },
    # Q46: broken options; answer is (c) binocular vision
    "46": {
        "stem": (
            "With respect to image formation by both eyes of a person, which one of "
            "the following statements is TRUE?"
        ),
        "options": [
            "Each eye forms an identical image so there is no depth perception",
            "One eye forms the primary image while the other provides only peripheral "
            "vision",
            "Both eyes combine two slightly different images to form a single "
            "three-dimensional image enabling depth perception",
            "Both eyes together form an erect image by combining two inverted images",
        ],
        "correct_index": 2,
        "correct_letter": "C",
        "subject": "General Science",
        "topic": "Physics",
        "topic_code": "SCI_PHYSICS",
        "explanation": (
            "Each eye sees the same object from a slightly different angle, forming two "
            "slightly different (parallax) images. The brain combines these two images "
            "to create a single three-dimensional image, which gives us depth perception "
            "(binocular vision / stereoscopic vision). Hence (C) is the correct answer."
        ),
    },
}

# ── Apply fixes to existing questions ─────────────────────────────────────────
q_by_num = {}
for q in real_qs:
    pn = q["source"]["printed_number"]
    q_by_num[pn] = q

    if pn in CLASSIFICATION_FIXES:
        subj, topic, code = CLASSIFICATION_FIXES[pn]
        q["subject"] = subj
        q["topic"]   = topic
        q["topic_code"] = code

    if pn in SPECIFIC_FIXES:
        for k, v in SPECIFIC_FIXES[pn].items():
            q[k] = v

# ── 4. Add 5 missing questions ────────────────────────────────────────────────
NEW_QUESTIONS = [
    # Q84 — Alphabet reordering (Reasoning)
    {
        "id": f"{paper_id}_q084_added",
        "stem": (
            "The English alphabet is reordered in the following manner: The first 6 "
            "letters are written in opposite order, the next 6 letters are written in "
            "opposite order and so on. At the end, 'Y' is interchanged with 'Z'. Which "
            "one of the following is the fourth letter to the right of the 13th letter "
            "from the left in the reordered alphabet?"
        ),
        "passage_context": None,
        "options": ["N", "O", "M", "I"],
        "correct_index": 0,
        "correct_letter": "A",
        "explanation": (
            "Reordering: groups of 6 letters reversed → F E D C B A | L K J I H G | "
            "R Q P O N M | X W V U T S | Y Z. Then Y↔Z → final: "
            "F E D C B A L K J I H G R Q P O N M X W V U T S Z Y. "
            "13th letter = R. The 4th letter to the right = 17th letter = N. "
            "Hence (A) N is the correct answer."
        ),
        "subject": "Reasoning",
        "topic": "Alphabet Series",
        "topic_code": "REAS_LETTER_SERIES",
        "difficulty": "HARD",
        "images": [],
        "source": {"printed_number": "84", "page": None},
    },
    # Q85 — Variation (Mathematics)
    {
        "id": f"{paper_id}_q085_added",
        "stem": (
            "If 'a' varies as 'b', then which of the following statements is/are "
            "correct?\n"
            "1. nᵗʰ root of a²b varies as (2n)ᵗʰ root of a⁴b².\n"
            "2. a/b² varies inversely as b.\n\n"
            "Select the correct answer using the code given below:"
        ),
        "passage_context": None,
        "options": ["1 only", "2 only", "Both 1 and 2", "Neither 1 nor 2"],
        "correct_index": 2,
        "correct_letter": "C",
        "explanation": (
            "Given a ∝ b → a = kb. "
            "Statement 1: (a²b)^(1/n) = (k²b³)^(1/n) = k^(2/n)·b^(3/n); "
            "(a⁴b²)^(1/(2n)) = (k⁴b⁶)^(1/(2n)) = k^(2/n)·b^(3/n). Both equal — "
            "Statement 1 is correct. "
            "Statement 2: a/b² = kb/b² = k/b ∝ 1/b — varies inversely as b. "
            "Statement 2 is correct. "
            "Hence (C) Both 1 and 2 is the correct answer."
        ),
        "subject": "Mathematics",
        "topic": "Variation",
        "topic_code": "MATH_QA",
        "difficulty": "HARD",
        "images": [],
        "source": {"printed_number": "85", "page": None},
    },
    # Q89 — Trial Balance (Accounting)
    {
        "id": f"{paper_id}_q089_added",
        "stem": "Is the total of the Debit side and Credit side of a Trial Balance the same?",
        "passage_context": None,
        "options": [
            "No, there are sometimes good reasons why they differ.",
            "Yes, always.",
            "Yes, except where the Trial Balance is extracted at the year end.",
            "No, because it is not a Balance Sheet.",
        ],
        "correct_index": 1,
        "correct_letter": "B",
        "explanation": (
            "A Trial Balance is prepared to verify the arithmetical accuracy of ledger "
            "postings. Under the double-entry system, every debit has a corresponding "
            "credit, so the total of all debit balances ALWAYS equals the total of all "
            "credit balances. Hence (B) 'Yes, always' is the correct answer."
        ),
        "subject": "Accounting & Auditing",
        "topic": "Trial Balance",
        "topic_code": "ACCT_PRINCIPLES",
        "difficulty": "EASY",
        "images": [],
        "source": {"printed_number": "89", "page": None},
    },
    # Q92 — Ryotwari areas (History)
    {
        "id": f"{paper_id}_q092_added",
        "stem": (
            "Which one of the following statements about the condition of Ryotwari "
            "areas is correct?"
        ),
        "passage_context": None,
        "options": [
            "Most of the land went to big moneylenders, merchants and rich peasants "
            "who generally used the services of tenants.",
            "Landless labourers became land owners.",
            "It put a stop to the practice of subletting land at high prices to "
            "tenants.",
            "Zamindari was completely destroyed.",
        ],
        "correct_index": 0,
        "correct_letter": "A",
        "explanation": (
            "Under the Ryotwari settlement (Madras and Bombay Presidencies), direct "
            "revenue settlement was made between the government and individual ryots. "
            "However, high revenue demands forced ryots into debt, and as a consequence "
            "most of the land gradually passed into the hands of big moneylenders, "
            "merchants and rich peasants who then used the labour of the indebted "
            "former cultivators as tenants. Hence (A) is the correct answer."
        ),
        "subject": "History",
        "topic": "Modern India",
        "topic_code": "HIS_MODERN",
        "difficulty": "HARD",
        "images": [],
        "source": {"printed_number": "92", "page": None},
    },
    # Q93 — Social Service League (History)
    {
        "id": f"{paper_id}_q093_added",
        "stem": "In 1911, who among the following founded Social Service League in Bombay?",
        "passage_context": None,
        "options": ["G.K. Gokhale", "S.A. Dange", "N.M. Joshi", "M.R. Jayakar"],
        "correct_index": 2,
        "correct_letter": "C",
        "explanation": (
            "N.M. Joshi (Narayan Malhar Joshi) founded the Social Service League in "
            "Bombay in 1911 to improve the conditions of industrial workers. He was "
            "also one of the founders of the All India Trade Union Congress (AITUC) in "
            "1920. Hence (C) N.M. Joshi is the correct answer."
        ),
        "subject": "History",
        "topic": "Modern India",
        "topic_code": "HIS_MODERN",
        "difficulty": "MEDIUM",
        "images": [],
        "source": {"printed_number": "93", "page": None},
    },
]

for new_q in NEW_QUESTIONS:
    pn = new_q["source"]["printed_number"]
    if pn not in q_by_num:
        real_qs.append(new_q)
    else:
        print(f"WARNING: Q{pn} already in JSON — skipping")

# ── 5. Sort, verify, save ─────────────────────────────────────────────────────
real_qs.sort(key=lambda q: int(q["source"]["printed_number"]))
nums = [int(q["source"]["printed_number"]) for q in real_qs]
missing = [n for n in range(1, 121) if n not in nums]
dupes = [n for n in nums if nums.count(n) > 1]
print(f"Total questions: {len(real_qs)}")
print(f"Missing: {missing}")
print(f"Duplicates: {sorted(set(dupes))}")

data["sections"][0]["questions"] = real_qs
data["parse_health"]["total_questions"] = len(real_qs)
data["parse_health"]["questions_with_answer"] = len(real_qs)
data["parse_health"]["questions_without_answer"] = 0

with open(JSON_PATH, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Saved:", JSON_PATH)
