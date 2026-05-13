#!/usr/bin/env python3
"""Fix remaining misclassified Geography questions in EPFO PYQ JSONs."""
import json, glob, re
from pathlib import Path

SEEDS = Path(__file__).resolve().parent.parent / "seeds" / "pyq" / "upsc"

# Specific stem→correct classification overrides
OVERRIDES = {
    "Factors determining movement of Africans": ("English", "Reading Comprehension", "ENG_RC"),
    "Kisan Sabha Movement": ("History", "Modern India & Freedom Struggle", "HIS_MODERN"),
    "Namami Gange": ("Indian Economy", "Government Schemes", "ECON_SCHEMES"),
    "consequence of deforestation": ("General Science", "Science & Technology", "SCI_TECH"),
    "bitter fights between": ("English", "Sentence Arrangement", "ENG_ARRANGE"),
    "agroecological region": ("English", "Reading Comprehension", "ENG_RC"),
    "decline in minor millet": ("English", "Reading Comprehension", "ENG_RC"),
    "Kautilya in his Arthashastra": ("History", "Ancient & Medieval India", "HIS_ANCIENT"),
    "Population change in an area": ("Indian Economy", "Macroeconomics", "ECON_MACRO"),
    "District Planning Committee": ("Indian Polity", "Constitution & Governance", "POL_CONSTITUTION"),
    "daroga was nominated": ("History", "Modern India & Freedom Struggle", "HIS_MODERN"),
    "eastern ghats and 15": ("English", "Reading Comprehension", "ENG_RC"),
}

fixed = 0
for f in sorted(glob.glob(str(SEEDS / "**/*.json"), recursive=True)):
    with open(f) as fh:
        doc = json.load(fh)
    changed = False
    for q in doc["sections"][0]["questions"]:
        if q.get("subject") != "Geography":
            continue
        stem = q.get("stem", "").lower()
        # Check if it's actually geography
        geo_kw = ["geograph", "river", "mountain", "monsoon", "climate",
                   "soil", "himalaya", "plateau", "ocean", "tropic",
                   "western ghats", "eastern ghats", "census", "mineral"]
        if any(kw in stem for kw in geo_kw):
            continue
        # Apply override
        for key, (subj, topic, code) in OVERRIDES.items():
            if key.lower() in stem:
                q["subject"] = subj
                q["topic"] = topic
                q["topic_code"] = code
                fixed += 1
                changed = True
                break
        else:
            # Generic fix for remaining
            q["subject"] = "General Studies"
            q["topic"] = "Miscellaneous"
            q["topic_code"] = "GS_MISC"
            fixed += 1
            changed = True
    if changed:
        with open(f, "w") as fh:
            json.dump(doc, fh, indent=2, ensure_ascii=False)

print(f"Fixed {fixed} misclassified Geography questions")
