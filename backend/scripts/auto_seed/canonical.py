"""Canonical subject strings and Schema B → Schema A transcoder.

Why this exists
---------------
The pool has accumulated two schemas and ~7 redundant subject strings
because chat-generated batches landed alongside pipeline-applied batches.
This module is the single source of truth for normalisation so every
future generation flows into one canonical shape.

Schema A (canonical, what apply_batch / dedup / taxonomy-sync understand):
    {"stem": "...", "options": [{"option_text": "...", "is_correct": bool}, ...],
     "correct_letter": "A"|"B"|"C"|"D", "subject", "topic", "topic_code",
     "difficulty": "EASY"|"MEDIUM"|"HARD", "effort_tier": "A"|"B"|"C",
     "staleness_risk": 0, "explanation": "..."}

Schema B (chat-generated, must be transcoded on ingest):
    {"text": "...", "options": [{"key": "A", "text": "..."}, ...],
     "correct": "A", "difficulty": "easy", "effort_tier": "tier1",
     "explanation": "..."}
"""
from __future__ import annotations

CANONICAL_SUBJECT: dict[str, str] = {
    # Identity (canonical strings map to themselves)
    "Quantitative Aptitude": "Quantitative Aptitude",
    "Reasoning": "Reasoning",
    "English": "English",
    "Vocabulary": "Vocabulary",
    "Physics": "Physics",
    "Chemistry": "Chemistry",
    "Biology": "Biology",
    "History": "History",
    "Polity": "Polity",
    "Geography": "Geography",
    "Economics": "Economics",
    "General Knowledge": "General Knowledge",
    "Environment": "Environment",
    # Aliases → canonical
    "Quant": "Quantitative Aptitude",
    "Logical Reasoning": "Reasoning",
    "English Language": "English",
    "Indian Polity": "Polity",
    "Polity & Law": "Polity",
    "Political Science": "Polity",
    "Environment & Ecology": "Environment",
    "Modern History": "History",
    "General Awareness": "General Knowledge",
}

# Subject → on-disk folder slug (matches existing backend/seeds/static_gk/<slug>/)
SUBJECT_FOLDER: dict[str, str] = {
    "Quantitative Aptitude": "quant",
    "Reasoning": "reasoning",
    "English": "english",
    "Vocabulary": "vocabulary",
    "Physics": "physics",
    "Chemistry": "chemistry",
    "Biology": "biology",
    "History": "history",
    "Polity": "polity",
    "Geography": "geography",
    "Economics": "economics",
    "General Knowledge": "general_knowledge",
    "Environment": "environment",
}

# Topic-code prefix → expected canonical subject (used to repair MISSING subjects)
PREFIX_TO_SUBJECT: dict[str, str] = {
    "QNT": "Quantitative Aptitude",
    "REAS": "Reasoning",
    "ENG": "English",
    "VOCAB": "Vocabulary",
    "PHY": "Physics",
    "CHEM": "Chemistry", "CHE": "Chemistry",
    "BIO": "Biology",
    "HIS": "History",
    "POL": "Polity",
    "GEO": "Geography",
    "ECO": "Economics",
    "GK": "General Knowledge", "GA": "General Knowledge",
    "ENV": "Environment",
    "ST": "Physics",  # legacy "Science & Technology" — fold into Physics
    "CS": "General Knowledge",  # rare; keep alive
}

_DIFF_NORMALISE = {
    "easy": "EASY", "medium": "MEDIUM", "hard": "HARD",
    "EASY": "EASY", "MEDIUM": "MEDIUM", "HARD": "HARD",
}
_TIER_NORMALISE = {
    "tier1": "A", "tier2": "B", "tier3": "C",
    "A": "A", "B": "B", "C": "C",
}
_LETTERS = ("A", "B", "C", "D", "E")


def canon_subject(raw: str | None) -> str | None:
    if not raw:
        return None
    return CANONICAL_SUBJECT.get(raw.strip(), raw.strip())


def subject_for_code(topic_code: str) -> str | None:
    if not topic_code:
        return None
    prefix = topic_code.split("_", 1)[0]
    return PREFIX_TO_SUBJECT.get(prefix)


def to_schema_a(q: dict) -> dict:
    """Return Schema A dict, accepting either Schema A or B input. Idempotent."""
    out = dict(q)

    # text → stem
    if "stem" not in out and "text" in out:
        out["stem"] = out.pop("text")

    # options [{key,text}] → [{option_text, is_correct}]
    correct_key = (out.get("correct_letter") or out.get("correct") or "").upper().strip()
    new_opts: list[dict] = []
    for opt in out.get("options") or []:
        if not isinstance(opt, dict):
            continue
        if "option_text" in opt and "is_correct" in opt:
            # already A
            new_opts.append({
                "option_text": opt["option_text"],
                "is_correct": bool(opt["is_correct"]),
            })
        elif "key" in opt and "text" in opt:
            new_opts.append({
                "option_text": opt["text"],
                "is_correct": opt["key"].upper().strip() == correct_key,
            })
    out["options"] = new_opts

    # correct → correct_letter (derived from is_correct flag, deterministic)
    if "correct" in out:
        out["correct_letter"] = out.pop("correct").upper().strip()
    if "correct_letter" not in out and new_opts:
        for i, o in enumerate(new_opts):
            if o["is_correct"]:
                out["correct_letter"] = _LETTERS[i]
                break

    # difficulty / effort_tier normalisation
    if out.get("difficulty"):
        out["difficulty"] = _DIFF_NORMALISE.get(out["difficulty"], out["difficulty"].upper())
    if out.get("effort_tier"):
        out["effort_tier"] = _TIER_NORMALISE.get(out["effort_tier"], out["effort_tier"].upper())

    # staleness_risk default
    out.setdefault("staleness_risk", 0)

    # Repair missing subject from topic_code prefix
    if not out.get("subject"):
        s = subject_for_code(out.get("topic_code", ""))
        if s:
            out["subject"] = s
    out["subject"] = canon_subject(out.get("subject"))

    return out


def to_schema_a_bundle(bundle: dict) -> dict:
    """Transcode an entire bundle (file) in-place."""
    out = dict(bundle)
    out["subject"] = canon_subject(out.get("subject"))
    out["questions"] = [to_schema_a(q) for q in out.get("questions", [])]
    return out
