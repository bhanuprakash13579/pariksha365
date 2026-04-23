#!/usr/bin/env python3
"""Classify the 1966 parsed EPFO questions into module-scoped subject/topic/topic_code.

Strategy:
  * Part Roman numeral (I-XVI) -> subject.
  * Within each subject, keyword-match the section label into a small topic bucket.
    This gives ~6-12 topics per subject, enough density for the weak-topic matcher
    to recommend related questions when a user gets one wrong.
"""
import json
import re
from pathlib import Path

IN = Path("/tmp/epfo_questions.json")
OUT = Path("/tmp/epfo_classified.json")

# Part -> subject label shown in the EPFO module UI.
PART_SUBJECT = {
    "I":    "APFC Role & Exam",
    "II":   "EPF Act 1952",
    "III":  "EPS 1995",
    "IV":   "EDLI 1976",
    "V":    "SS Code 2020",
    "VI":   "Labour Laws",
    "VII":  "Indian Economy",
    "VIII": "Indian Polity",
    "IX":   "Accounting",
    "X":    "History & Labour Movement",
    "XI":   "Science & Technology",
    "XII":  "Current Affairs",
    "XIII": "Mixed Revision",
    "XV":   "Indian Geography",
    "XVI":  "Gap Patches",
}

# Short tag used inside topic_code so codes stay readable.
PART_TAG = {
    "I":    "APFC",    "II":   "EPF",    "III":  "EPS",     "IV":   "EDLI",
    "V":    "SSCODE",  "VI":   "LABOUR", "VII":  "ECO",     "VIII": "POL",
    "IX":   "ACCT",    "X":    "HIST",   "XI":   "SCI",     "XII":  "CA",
    "XIII": "MIXED",   "XV":   "GEO",    "XVI":  "GAP",
}

# Per-subject topic buckets. First regex that matches (case-insensitive) against the
# section-label tail wins. Fallthrough bucket is "General".
TOPIC_RULES = {
    "I": [
        (r"apfc", "APFC Role"),
        (r"exam|pattern|syllabus|qualif", "Exam Pattern & Syllabus"),
    ],
    "II": [
        (r"applicab|scope|cover", "Applicability & Scope"),
        (r"definit|basic wage|wage ceiling", "Definitions & Wages"),
        (r"contribut|admin charge|edli charge", "Contributions & Admin Charges"),
        (r"cbt|board of trust|structure|appoint|commiss", "CBT & Structure"),
        (r"offenc|penalt|prosecu|damage|section 14|s\.14|14b|14a", "Offences & Penalties"),
        (r"tribunal|appeal|review|7b|7i", "Tribunal & Appeals"),
        (r"enforc|inspec|7a|recover|attach|certif|7q|interest", "7A Enforcement & Recovery"),
        (r"uan|form|withdraw|transf|claim|kyc|ecr|trrn", "UAN · Forms · Claims"),
        (r"digital|it|e-?sewa|portal|app|tech|ai", "EPFO Digital & IT"),
        (r"insolv|ibc|liquid|resolut", "Insolvency & IBC"),
        (r"exempt|relax|trust", "Exempted Establishments"),
        (r"scenario|case|ult", "Scenarios & Case Studies"),
    ],
    "III": [
        (r"applicab|elig|scope|cover", "Applicability & Eligibility"),
        (r"contribut|1\.16|8\.33|9\.49", "Contributions"),
        (r"formula|commut|pensionable", "Pension Formula"),
        (r"higher|option|2014|moharir|ep s-95", "Higher Pension Option"),
        (r"widow", "Widow Pension"),
        (r"orphan|child", "Orphan / Child Pension"),
        (r"disabl|perman", "Disablement Pension"),
        (r"deferred|early|reduct", "Early / Deferred Pension"),
        (r"withdraw|scheme certif", "Withdrawal / Scheme Certificate"),
        (r"international|iw|ssa", "International Worker Pension"),
        (r"scenario|case|ult", "Scenarios & Case Studies"),
    ],
    "IV": [
        (r"applicab|scope|cover", "Applicability & Scope"),
        (r"benefit|formula|7 lakh|claim amount|bonus|₹7|₹2\.5", "Benefit & Formula"),
        (r"wage|ceiling|basic", "Wages for EDLI"),
        (r"claim|form 5if|settle|process", "Claim Process"),
        (r"contribut|admin|0\.01|0\.5", "Contributions & Admin Charges"),
        (r"scenario|case|ult", "Scenarios & Case Studies"),
    ],
    "V": [
        (r"applicab|scope|cover|operative|enforce|notific", "Scope & Implementation"),
        (r"benefit|welfare", "Benefits"),
        (r"gig|platform|aggregator|fixed.term", "Gig / Platform / FTE"),
        (r"matern|chapter vi", "Maternity"),
        (r"unorgan|building|construc", "Unorganised & BOCW"),
        (r"social security fund|ssb|board|nssb|cess", "Social Security Board & Cess"),
        (r"repeal|chapter|chap|13 act|9 act", "Code Structure & Repealed Acts"),
        (r"scenario|case|ult|deep", "Scenarios & Case Studies"),
    ],
    "VI": [
        (r"id act|industrial dispute|1947", "Industrial Disputes Act 1947"),
        (r"gratuity", "Gratuity Act"),
        (r"bonus|13.*act|1965", "Payment of Bonus Act"),
        (r"minimum wage|1948", "Minimum Wages Act"),
        (r"employ.* comp|ec act|workmen comp|1923", "Employees Compensation Act"),
        (r"contract labour|cll?ra|1970", "Contract Labour Act"),
        (r"matern|1961", "Maternity Benefit Act"),
        (r"trade union|1926|ntuc|aituc", "Trade Unions"),
        (r"working hours|factor|1948", "Factories Act / Working Hours"),
        (r"equal rem|1976|equal pay", "Equal Remuneration"),
        (r"osh|occupation|safety", "OSH & Welfare"),
        (r"payment of wage|1936", "Payment of Wages Act"),
        (r"appren|training", "Apprentices Act"),
        (r"scenario|case|ult", "Scenarios & Case Studies"),
    ],
    "VII": [
        (r"macro|gdp|gnp|ndp", "Macro Basics"),
        (r"budget|fiscal|frbm|deficit", "Budget & Fiscal"),
        (r"federal|finance comm|devolution", "Fiscal Federalism"),
        (r"gst|indirect tax|direct tax|excise", "Taxation"),
        (r"rbi|repo|reverse repo|crr|slr|monetary", "Banking & Monetary Policy"),
        (r"inflation|cpi|wpi", "Inflation"),
        (r"external|forex|bop|rupee|trade", "External Sector"),
        (r"ilo|international|imf|world bank", "International Economic Bodies"),
        (r"poverty|employment|nrega|mgnrega|skill", "Poverty & Employment"),
    ],
    "VIII": [
        (r"constitut|preamble|schedule|article", "Constitution"),
        (r"fundamental right|fr\b|art 14|art 19|art 21", "Fundamental Rights"),
        (r"dpsp|directive", "DPSP"),
        (r"writ|habeas|mandamus|certiorari|prohibition|quo warranto", "Writs"),
        (r"money bill|finance bill|110|art 110", "Money Bill & Finance Bill"),
        (r"parliament|speaker|rajya|lok|art 108|joint sitting", "Parliament"),
        (r"judiciary|supreme court|high court|art 32|art 226|collegium", "Judiciary"),
        (r"president|vice.president|governor|art 53|art 72|art 74", "Executive"),
        (r"emergency|art 352|art 356|art 360", "Emergency Provisions"),
        (r"legal maxim|latin", "Legal Maxims"),
        (r"citizen|art 5|art 11", "Citizenship"),
        (r"amendment|basic structure|keshav", "Amendments & Basic Structure"),
        (r"local|panchayat|municip|74th|73rd", "Local Government"),
    ],
    "IX": [
        (r"fundament|basic|accounting equation|double entry", "Fundamentals"),
        (r"statement|balance sheet|p&?l|income statement", "Financial Statements"),
        (r"ratio|liquidity|solvency|profitab|turnover", "Financial Ratios"),
        (r"audit|standard on audit|sa ", "Auditing"),
        (r"cost|overhead|break.even|standard cost", "Cost Accounting"),
        (r"investing|financing|operating|cash flow", "Cash Flow"),
        (r"csr|section 135|social resp", "CSR"),
        (r"depreciat|deprec", "Depreciation"),
        (r"ifrs|ind.as|gaap|accounting standard", "Accounting Standards"),
    ],
    "X": [
        (r"freedom|gandhi|dandi|quit india|1857|revolt|sepoy|non.cooperat|civil diso|swadesh|inc|congress", "Freedom Struggle"),
        (r"labour movement|trade union|aituc|ntuc|strike|bombay mill|1918|1920|1947 nat comm", "Labour Movement"),
        (r"ilo|international lab|convention|philadelphia|1919", "ILO History"),
        (r"five year|planning|nehru|mahalanobis", "Planning Era"),
    ],
    "XI": [
        (r"indoor air|pollut|environment", "Environment & Pollution"),
        (r"physic|newton|light|electric|magn|thermo|sound", "Physics"),
        (r"chemi|acid|alka|metal|organic|periodic", "Chemistry"),
        (r"biolog|cell|dna|blood|disease|virus|vaccine|health", "Biology & Health"),
        (r"comput|ai|ml|cyber|it\b|software|internet|cloud|blockchain", "Computing & IT"),
        (r"osh|safety|occupational|ergonomic", "Occupational Health"),
        (r"space|isro|sattel|mission", "Space & Defence"),
    ],
    "XII": [
        (r"epfo updat|epfo recent|face auth|cpfc|cbt |higher pens", "EPFO Recent Updates"),
        (r"case law|judgment|supreme court|high court|2024|2025", "Recent Case Law"),
        (r"scheme|yojana|pm |abha|ayushman|pmjjby|atal", "Government Schemes"),
        (r"internat|g20|g7|un |imf|world bank|ilo", "International Affairs"),
        (r"econ|gdp|budget|rbi|fiscal|inflation|repo", "Economy Current"),
        (r"sport|award|padma|nobel|oscar|bharat ratna", "Awards & Sports"),
        (r"defence|space|missile|isro", "Defence & Space"),
        (r"env|climate|cop|g20|unep|sdg", "Environment Current"),
    ],
    "XIII": [
        (r"final mock", "Final Mock"),
        (r"judgment spot", "Judgment Spot"),
        (r"mixed revis", "Mixed Revision"),
        (r"full.length", "Full-Length Mock"),
    ],
    "XV": [
        (r"physic|relief|mountain|plateau|river|climate", "Physical Geography"),
        (r"econom|resource|mineral|industr|crop", "Economic Geography"),
    ],
    "XVI": [
        (r"insurance|irda", "Insurance"),
        (r"art|culture|dance|music|painting|folk|festival", "Art & Culture"),
        (r"tribal|rebellion|santhal|munda|bhil|birsa", "Tribal Rebellions"),
    ],
}


def parse_section(section: str):
    m = re.match(r"^([IVXLC]+)\.(.+)$", section.strip())
    if not m:
        return None, section.strip()
    return m.group(1), m.group(2).strip()


def slugify(s: str) -> str:
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]+", "_", s).strip("_")
    return s or "MISC"


def pick_topic(part: str, tail: str, stem: str):
    """Return (topic_label, topic_code). First keyword rule that matches the tail OR the stem wins."""
    rules = TOPIC_RULES.get(part, [])
    haystack = f"{tail}\n{stem}".lower()
    for pattern, topic in rules:
        if re.search(pattern, haystack, re.IGNORECASE):
            return topic, slugify(topic)
    return "General", "GENERAL"


def main():
    qs = json.load(open(IN))
    out = []
    subject_count = {}
    topic_count = {}
    subject_topic_count = {}  # (subject, topic) -> count

    for q in qs:
        part, tail = parse_section(q["section"])
        if part not in PART_SUBJECT:
            subject = "Mixed Revision"
            tag = "MIXED"
            part = "XIII"
        else:
            subject = PART_SUBJECT[part]
            tag = PART_TAG[part]
        topic_label, topic_slug = pick_topic(part, tail, q["stem"])
        topic_code = f"EPFO_{tag}_{topic_slug}"[:80]

        options = [
            {"option_text": q["options"]["A"], "is_correct": q["correct_letter"] == "A"},
            {"option_text": q["options"]["B"], "is_correct": q["correct_letter"] == "B"},
            {"option_text": q["options"]["C"], "is_correct": q["correct_letter"] == "C"},
            {"option_text": q["options"]["D"], "is_correct": q["correct_letter"] == "D"},
        ]

        out.append({
            "qnum": q["qnum"],
            "section": q["section"],
            "subject": subject,
            "topic": topic_label,
            "topic_code": topic_code,
            "stem": q["stem"],
            "options": options,
            "correct_letter": q["correct_letter"],
            "explanation": q["explanation"],
        })

        subject_count[subject] = subject_count.get(subject, 0) + 1
        topic_count[topic_code] = topic_count.get(topic_code, 0) + 1
        key = (subject, topic_label)
        subject_topic_count[key] = subject_topic_count.get(key, 0) + 1

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(out)} classified questions -> {OUT}")
    print()
    print("=== Subject distribution ===")
    for s, c in sorted(subject_count.items(), key=lambda kv: -kv[1]):
        print(f"  {c:4d}  {s}")
    print()
    print(f"=== Per-subject topic density ({len(topic_count)} topic codes) ===")
    last_subj = None
    for (subj, topic), c in sorted(subject_topic_count.items(), key=lambda kv: (kv[0][0], -kv[1])):
        if subj != last_subj:
            print(f"\n  [{subj}]")
            last_subj = subj
        print(f"    {c:4d}  {topic}")
    singletons = [tc for tc, c in topic_count.items() if c == 1]
    print(f"\nSingleton topic codes: {len(singletons)}")


if __name__ == "__main__":
    main()
