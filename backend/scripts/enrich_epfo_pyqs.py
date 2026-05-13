#!/usr/bin/env python3
"""Enrich EPFO PYQ JSON files with explanations from compiled text files
and fix subject/topic classification.

Sources:
  /home/bhanu/Documents/pariksha/UPSC/EPFO/PYQ_2025_compiled_text.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/PYQ_2023_compiled_text.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/EOAO_2023_text.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/EOAO_2025_analysis.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/EOAO_2023_analysis.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/DEEP_Analysis_NonLabour_Subjects.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/PYQ_2020_text.txt
  /home/bhanu/Documents/pariksha/UPSC/EPFO/PYQ_SetB_2023_Jul_text.txt
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

EPFO_DIR = Path("/home/bhanu/Documents/pariksha/UPSC/EPFO")
SEEDS_DIR = Path(__file__).resolve().parent.parent / "seeds" / "pyq" / "upsc"

# ── Subject/Topic classification keywords ──────────────────────────────────
# Order matters — most specific first
CLASSIFICATION_RULES: list[tuple[str, str, str, list[str]]] = [
    # (subject, topic, topic_code, keywords_in_stem)
    ("Labour Laws & Social Security", "EPF Act & Schemes", "EPFO_EPF_ACT",
     ["epf ", "epfo", "provident fund", "section 7a", "section 7q", "section 14",
      "cpfc", "apfc", "basic wages", "contribution", "central board of trustees",
      "cbt", "employees' provident", "auto-settlement", "eli scheme",
      "employment linked incentive", "spree"]),
    ("Labour Laws & Social Security", "EPS & EDLI", "EPFO_EPS_EDLI",
     ["pension scheme", "eps ", "edli", "employees' deposit", "family pension"]),
    ("Labour Laws & Social Security", "Social Security Code", "EPFO_SS_CODE",
     ["social security code", "code on social security", "gig worker",
      "platform worker", "ss code", "code on wages"]),
    ("Labour Laws & Social Security", "Industrial Relations", "EPFO_IR",
     ["industrial dispute", "trade union", "standing order", "retrench",
      "strike", "lockout", "contract labour", "inter-state migrant",
      "grievance redressal committee"]),
    ("Labour Laws & Social Security", "Factories Act", "EPFO_FACTORIES",
     ["factory act", "factories act", "hazardous process",
      "safety committee", "chief inspector"]),
    ("Labour Laws & Social Security", "Wages & Benefits", "EPFO_WAGES",
     ["minimum wage", "payment of wages", "bonus act", "gratuity",
      "maternity benefit", "equal remuneration", "workmen's compensation"]),
    ("Labour Laws & Social Security", "Social Protection", "EPFO_SOCIAL_PROT",
     ["social protection", "unorganised workers", "nsssb", "esi ",
      "employees' state insurance", "wspr", "ilo "]),
    ("Accounting & Auditing", "Accounting Principles", "ACCT_PRINCIPLES",
     ["accounting", "debit", "credit", "balance sheet", "trial balance",
      "journal entry", "double entry", "ledger", "gaap", "ind as",
      "conservatism", "going concern", "accrual", "matching concept",
      "cost or net realisable", "inventory valuation", "fifo",
      "revenue expenditure", "capital expenditure", "error of principle",
      "error of commission", "suspense account", "nominal account"]),
    ("Accounting & Auditing", "Auditing", "ACCT_AUDITING",
     ["audit", "auditor", "sa 230", "cag ", "verification in auditing",
      "audit documentation"]),
    ("Accounting & Auditing", "Insurance", "ACCT_INSURANCE",
     ["insurance", "indemnity", "subrogation", "mitigation", "utmost good faith"]),
    ("Accounting & Auditing", "Financial Statements", "ACCT_FIN_STMT",
     ["operating profit", "net profit", "depreciation", "cost sheet",
      "cost of inventory", "reserves", "provision"]),
    ("Indian Polity", "Constitution & Governance", "POL_CONSTITUTION",
     ["constitution", "fundamental right", "dpsp", "directive principle",
      "article ", "schedule of", "part-", "preamble", "citizenship",
      "uniform civil code"]),
    ("Indian Polity", "Parliament & Legislature", "POL_PARLIAMENT",
     ["parliament", "lok sabha", "rajya sabha", "legislative power",
      "residuary power", "union list", "concurrent list", "state list",
      "ordinance"]),
    ("Indian Polity", "Judiciary", "POL_JUDICIARY",
     ["supreme court", "high court", "contempt", "curative petition",
      "advisory jurisdiction", "chief justice"]),
    ("Indian Polity", "Constitutional Bodies", "POL_CONST_BODIES",
     ["election commission", "finance commission", "gst council",
      "attorney general", "comptroller", "rti act", "information commissioner",
      "nhrc", "ganhri", "evm ", "vvpat"]),
    ("Indian Polity", "Governor & State Govt", "POL_STATE_GOVT",
     ["governor", "state government", "state legislature"]),
    ("Indian Economy", "Macroeconomics", "ECON_MACRO",
     ["gdp", "inflation", "core inflation", "fiscal", "monetary policy",
      "repo rate", "crr", "slr", "rbi ", "budget", "fiscal deficit"]),
    ("Indian Economy", "Development Finance", "ECON_DEV_FIN",
     ["ifci", "icici", "idbi", "nabfid", "development financial",
      "nabard", "sidbi"]),
    ("Indian Economy", "Trade & International", "ECON_INTL",
     ["imf", "world bank", "wto", "fdi", "trade", "brics",
      "currency swap", "saarc", "asean"]),
    ("Indian Economy", "Government Schemes", "ECON_SCHEMES",
     ["nishtha", "pm poshan", "smile scheme", "bioe3", "zero defect",
      "skill development", "make in india", "digital india",
      "e-vidhan", "nev "]),
    ("History", "Ancient & Medieval India", "HIS_ANCIENT",
     ["natyashastra", "bhimbetka", "ajanta", "temple", "pagoda",
      "mahayana", "buddhis", "jainism", "maurya", "gupta",
      "vedic", "indus valley", "mughal", "sultanate", "chola",
      "pallava", "sittannavasal", "brihadeshwara", "konark",
      "khajuraho"]),
    ("History", "Modern India & Freedom Struggle", "HIS_MODERN",
     ["freedom struggle", "non-cooperation", "british", "rebellion",
      "home rule", "congress", "gandhi", "nehru", "tilak",
      "besant", "quit india", "jallianwala", "dandi", "1857",
      "muttadar", "visakhapatnam", "gudem", "santhal", "deccan revolt",
      "kherwar", "rampa"]),
    ("Geography", "Physical Geography", "GEO_PHYSICAL",
     ["himalaya", "river", "monsoon", "plateau", "ocean current",
      "western ghats", "eastern ghats", "climate zone", "soil",
      "earthquake", "tectonic"]),
    ("Geography", "Indian Geography", "GEO_INDIA",
     ["census", "population", "sex ratio", "state wise", "district",
      "mineral", "coal", "iron ore"]),
    ("General Science", "Physics", "SCI_PHYSICS",
     ["electromagnetic", "frequency", "microwave", "infrared",
      "gps ", "trilateration", "pleural cavity", "awacs",
      "drone jam", "power", "electricity", "resistance", "bulb"]),
    ("General Science", "Chemistry", "SCI_CHEMISTRY",
     ["carbolic acid", "phenol", "amine", "fatty acid", "photochemical smog",
      "acid", "base", "salt", "periodic table", "copper sulphate",
      "tartaric", "magnesium"]),
    ("General Science", "Biology", "SCI_BIOLOGY",
     ["dna", "gene", "chlorophyll", "photosynthesis", "digestion",
      "velamen", "tissue", "cell"]),
    ("General Science", "Science & Technology", "SCI_TECH",
     ["spacex", "falcon", "dragon", "isro", "chandrayaan",
      "satellite", "rocket", "vaccine"]),
    ("Computer Awareness", "AI & Emerging Tech", "COMP_AI",
     ["chatgpt", "artificial intelligence", "llm", "large language model",
      "gpu", "machine learning", "ai model", "blockchain"]),
    ("Computer Awareness", "Computer Fundamentals", "COMP_FUND",
     ["html", "networking", "osi layer", "mime", "binary",
      "cell referenc", "linker", "spool", "cpu", "ram", "rom",
      "operating system"]),
    ("English", "Reading Comprehension", "ENG_RC",
     ["passage", "comprehension", "africa is on the move"]),
    ("English", "Vocabulary", "ENG_VOCAB",
     ["meaning of", "synonym", "antonym", "cordial", "impugned",
      "egregious", "apostate", "corporeity", "platitude"]),
    ("English", "Grammar & Usage", "ENG_GRAMMAR",
     ["preposition", "phrasal verb", "tense", "modal", "article",
      "adjective order", "amidst", "amongst", "put in", "put out",
      "takes after", "sentence", "error"]),
    ("English", "Sentence Arrangement", "ENG_ARRANGE",
     ["rearrange", "s1", "p q r s", "jumble"]),
    ("Mathematics", "Quantitative Aptitude", "MATH_QA",
     ["percent", "profit", "loss", "interest", "speed", "time",
      "work", "ratio", "average", "probability", "lcm", "hcf",
      "clock", "angle", "triangle", "circle", "sequence",
      "arithmetic progression", "geometric"]),
    ("Current Affairs", "National Affairs", "CA_NATIONAL",
     ["padma bhushan", "padma shri", "award", "launched", "inaugurated",
      "dag hammarskjold", "fifa", "world cup", "olympic",
      "shinawatra", "thai pm"]),
]


def classify_question(stem: str, options_text: str = "") -> tuple[str, str, str]:
    """Return (subject, topic, topic_code) based on stem keywords."""
    combined = (stem + " " + options_text).lower()
    for subject, topic, code, keywords in CLASSIFICATION_RULES:
        if any(kw in combined for kw in keywords):
            return subject, topic, code
    return "General Studies", "Miscellaneous", "GS_MISC"


# ── Explanation parser ──────────────────────────────────────────────────────

def parse_explanations_from_compiled(text: str) -> dict[int, str]:
    """Parse Q.N Answer: X / Explanation: blocks from compiled EduTap PDFs.
    Returns {question_number: explanation_text}.
    """
    explanations: dict[int, str] = {}

    # Find the explanation section (after "Explanation" header, before end)
    expl_match = re.search(r'\n\s*Explanation\s*\n', text)
    if not expl_match:
        return explanations

    expl_text = text[expl_match.end():]

    # Split into Q blocks: Q1. Answer: X ... Q2. Answer: Y ...
    q_blocks = re.split(r'(?=Q\d+\.\s*Answer:\s*[A-Da-d])', expl_text)

    for block in q_blocks:
        m = re.match(r'Q(\d+)\.\s*Answer:\s*[A-Da-d]\s*\n\s*Explanation:\s*\n?(.*)',
                     block, re.DOTALL)
        if not m:
            continue
        qnum = int(m.group(1))
        raw = m.group(2).strip()

        # Clean: remove page markers, email/phone, difficulty level tags
        raw = re.sub(r'\f.*?\n', '\n', raw)
        raw = re.sub(r'hello@edutap\.co\.in', '', raw)
        raw = re.sub(r'\+91\s*\d{10}', '', raw)
        raw = re.sub(r'Difficulty Level:\s*(Easy|Moderate|Difficult)\s*$', '',
                     raw, flags=re.MULTILINE)
        # Remove trailing Q block start
        raw = re.sub(r'\nQ\d+\.\s*Answer:.*', '', raw, flags=re.DOTALL)
        # Collapse whitespace
        raw = re.sub(r'\n{3,}', '\n\n', raw).strip()

        if len(raw) > 20:
            explanations[qnum] = raw

    return explanations


def parse_explanations_from_2pass(text: str) -> dict[int, str]:
    """Parse two-pass files (questions first, explanations second).
    Used for PYQ_2023_compiled and EOAO_2023 texts.
    """
    explanations: dict[int, str] = {}

    # Find "Detailed Explanation" section
    split = re.search(r'[\n\f]\s*Detailed Explanation', text)
    if not split:
        return explanations

    expl_text = text[split.end():]

    # Split by Q.N) pattern
    q_blocks = re.split(r'(?=Q\.\d+\))', expl_text)

    for block in q_blocks:
        m = re.match(r'Q\.(\d+)\)(.*)', block, re.DOTALL)
        if not m:
            continue
        qnum = int(m.group(1))
        raw = m.group(2).strip()

        # Extract answer letter
        ans_match = re.search(r'Hence,?\s*[Oo]ption\s*([A-Da-d])\s*is\s*(?:the\s*)?correct', raw)

        # Clean up
        raw = re.sub(r'\f', '', raw)
        raw = re.sub(r'\n{3,}', '\n\n', raw).strip()

        if len(raw) > 15:
            explanations[qnum] = raw

    return explanations


def parse_analysis_classifications(text: str) -> dict[int, dict]:
    """Parse analysis files for subject distribution info.
    Returns {qnum: {subject, topic}} from lines like:
    Q1-5:   Fill in blanks — adjective order, modal verbs
    """
    classifications: dict[int, dict] = {}

    # Parse "Q<start>-<end>: Subject" lines
    for m in re.finditer(
        r'Q(\d+)-(\d+):\s*(.*?)(?:\n|$)', text
    ):
        start, end = int(m.group(1)), int(m.group(2))
        desc = m.group(3).strip()
        # Determine subject from description
        desc_lower = desc.lower()

        if any(w in desc_lower for w in ["english", "vocabulary", "passage",
                                          "comprehension", "fill in", "preposition",
                                          "phrasal", "sentence", "error"]):
            subj, topic = "English", "Grammar & Usage"
        elif any(w in desc_lower for w in ["labour", "epf", "social security",
                                            "maternity", "factories"]):
            subj, topic = "Labour Laws & Social Security", "Industrial Relations"
        elif any(w in desc_lower for w in ["math", "quantitative"]):
            subj, topic = "Mathematics", "Quantitative Aptitude"
        elif any(w in desc_lower for w in ["account", "audit", "insurance"]):
            subj, topic = "Accounting & Auditing", "Accounting Principles"
        elif any(w in desc_lower for w in ["science", "tech", "defence"]):
            subj, topic = "General Science", "Science & Technology"
        elif any(w in desc_lower for w in ["current", "scheme", "government"]):
            subj, topic = "Current Affairs", "National Affairs"
        elif any(w in desc_lower for w in ["econom", "finance", "development"]):
            subj, topic = "Indian Economy", "Macroeconomics"
        elif any(w in desc_lower for w in ["histor", "freedom", "ancient", "medieval"]):
            subj, topic = "History", "Modern India & Freedom Struggle"
        elif any(w in desc_lower for w in ["polit", "constitution", "rti",
                                            "governance", "electoral"]):
            subj, topic = "Indian Polity", "Constitution & Governance"
        elif any(w in desc_lower for w in ["computer"]):
            subj, topic = "Computer Awareness", "Computer Fundamentals"
        else:
            subj, topic = "General Studies", "Miscellaneous"

        for qn in range(start, end + 1):
            classifications[qn] = {"subject": subj, "topic": topic}

    return classifications


# ── Main enrichment ─────────────────────────────────────────────────────────

def enrich_paper(json_path: Path, compiled_path: Path | None,
                 analysis_path: Path | None, twopass: bool = False) -> dict:
    """Enrich a single PYQ JSON file with explanations and classifications."""
    with open(json_path) as f:
        doc = json.load(f)

    qs = doc["sections"][0]["questions"]
    stats = {"total": len(qs), "explanations_added": 0, "reclassified": 0,
             "already_had_explanation": 0}

    # Parse explanations from compiled text
    explanations: dict[int, str] = {}
    if compiled_path and compiled_path.exists():
        text = compiled_path.read_text(errors="replace")
        if twopass:
            explanations = parse_explanations_from_2pass(text)
        else:
            explanations = parse_explanations_from_compiled(text)
        print(f"  Parsed {len(explanations)} explanations from {compiled_path.name}")

    # Parse analysis classifications
    analysis_class: dict[int, dict] = {}
    if analysis_path and analysis_path.exists():
        atext = analysis_path.read_text(errors="replace")
        analysis_class = parse_analysis_classifications(atext)
        print(f"  Parsed {len(analysis_class)} classification hints from {analysis_path.name}")

    for i, q in enumerate(qs):
        qnum = i + 1  # 1-indexed question number

        # ── Add explanation if missing ──
        if not q.get("explanation") or q["explanation"].strip() == "":
            if qnum in explanations:
                q["explanation"] = explanations[qnum]
                stats["explanations_added"] += 1
        else:
            stats["already_had_explanation"] += 1

        # ── Reclassify subject/topic ──
        opts_text = " ".join(
            (o.get("option_text", "") if isinstance(o, dict) else str(o))
            for o in q.get("options", [])
        )
        new_subj, new_topic, new_code = classify_question(
            q.get("stem", ""), opts_text
        )

        old_subj = q.get("subject", "")
        old_topic = q.get("topic", "")

        # Only reclassify if the new classification is more specific
        # or the old one was clearly wrong
        if (new_subj != "General Studies" or old_subj in
                ("General Studies", "Geography", "Mathematics") and
                old_topic in ("Mixed", "Indian Geography", "Quantitative Aptitude",
                              "Science & Mathematics")):
            if new_subj != old_subj or new_topic != old_topic:
                q["subject"] = new_subj
                q["topic"] = new_topic
                q["topic_code"] = new_code
                stats["reclassified"] += 1
            else:
                # Same classification, just add topic_code
                if not q.get("topic_code"):
                    q["topic_code"] = new_code
        else:
            if not q.get("topic_code"):
                # Try to assign topic_code from existing subject/topic
                q["topic_code"] = new_code

    # Write back
    with open(json_path, "w") as f:
        json.dump(doc, f, indent=2, ensure_ascii=False)

    return stats


def main():
    print("=" * 60)
    print("EPFO PYQ Enrichment — Classification + Explanations")
    print("=" * 60)

    papers = [
        {
            "name": "APFC & EO/AO 2025",
            "json": SEEDS_DIR / "epfo-apfc/recruitment-test/EPFO-APFC-EO-AO-PYQ-2025.json",
            "compiled": EPFO_DIR / "PYQ_2025_compiled_text.txt",
            "analysis": EPFO_DIR / "EOAO_2025_analysis.txt",
            "twopass": False,
        },
        {
            "name": "APFC 2023 Set A",
            "json": SEEDS_DIR / "epfo-apfc/recruitment-test/EPFO-APFC-PYQ-2023-Set-A.json",
            "compiled": EPFO_DIR / "PYQ_2023_compiled_text.txt",
            "analysis": EPFO_DIR / "EOAO_2023_analysis.txt",
            "twopass": True,
        },
        {
            "name": "APFC 2023 Set B",
            "json": SEEDS_DIR / "epfo-apfc/recruitment-test/EPFO-APFC-PYQ-2023-Set-B.json",
            "compiled": EPFO_DIR / "PYQ_SetB_2023_Jul_text.txt",
            "analysis": EPFO_DIR / "EOAO_2023_analysis.txt",
            "twopass": False,
        },
        {
            "name": "APFC 2020",
            "json": SEEDS_DIR / "epfo-apfc/recruitment-test/EPFO-APFC-PYQ-2020.json",
            "compiled": EPFO_DIR / "PYQ_2020_text.txt",
            "analysis": None,
            "twopass": False,
        },
        {
            "name": "EO/AO 2025 (shared)",
            "json": SEEDS_DIR / "epfo-eo-ao/recruitment-test/EPFO-APFC-EO-AO-PYQ-2025.json",
            "compiled": EPFO_DIR / "PYQ_2025_compiled_text.txt",
            "analysis": EPFO_DIR / "EOAO_2025_analysis.txt",
            "twopass": False,
        },
        {
            "name": "EO/AO 2023",
            "json": SEEDS_DIR / "epfo-eo-ao/recruitment-test/EPFO-EO-AO-PYQ-2023.json",
            "compiled": EPFO_DIR / "EOAO_2023_text.txt",
            "analysis": EPFO_DIR / "EOAO_2023_analysis.txt",
            "twopass": True,
        },
    ]

    total_added = 0
    total_reclassified = 0

    for p in papers:
        print(f"\n{'─' * 50}")
        print(f"Processing: {p['name']}")
        if not p["json"].exists():
            print(f"  ⚠ JSON not found: {p['json']}")
            continue

        stats = enrich_paper(
            p["json"], p.get("compiled"), p.get("analysis"),
            twopass=p.get("twopass", False),
        )
        total_added += stats["explanations_added"]
        total_reclassified += stats["reclassified"]

        expl_now = stats["already_had_explanation"] + stats["explanations_added"]
        print(f"  ✓ {stats['total']} Qs total")
        print(f"    Explanations: {expl_now}/{stats['total']} "
              f"(+{stats['explanations_added']} added)")
        print(f"    Reclassified: {stats['reclassified']}")

    print(f"\n{'=' * 60}")
    print(f"TOTAL: +{total_added} explanations, {total_reclassified} reclassified")
    print("=" * 60)


if __name__ == "__main__":
    main()
