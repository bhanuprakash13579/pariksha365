"""Subject + topic classifier for parsed PYQ questions.

Two-stage classification:

1. **Subject** — the broad bucket (REASONING / QUANT / ENGLISH / GENERAL_AWARENESS
   / COMPUTER / DATA_INTERPRETATION). Determined primarily by the PDF family +
   question position in the paper, with the ``section_hint`` used as an override
   when the parser captured one. The per-family ordering rules are hand-coded
   from the official notifications and agree with all parsed samples.
2. **Topic** — a finer label within a subject (e.g. QUANT/simplification,
   REASONING/syllogism, GA/polity_constitution). Keyword-based, intentionally
   conservative: if no keyword matches, the topic is ``"UNCLASSIFIED"`` and the
   caller can choose to surface the question for manual review. Accuracy goal
   is 70–80 % coverage with near-zero false positives, which is enough to build
   a directional topic-frequency table for mock-test weighting.

Adding or refining labels is a small code change — expand the keyword lists
in ``_TOPIC_RULES`` below.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from scripts.pyq_ingest.parser import ParsedPaper, ParsedQuestion

Subject = str  # see _SUBJECT_CANON values
Topic = str

_SUBJECT_CANON = {
    "reasoning": "REASONING",
    "general intelligence": "REASONING",
    "intelligence": "REASONING",
    "quantitative": "QUANT",
    "quant": "QUANT",
    "mathematics": "QUANT",
    "mathematical": "QUANT",
    "maths": "QUANT",
    "data analysis": "DATA_INTERPRETATION",
    "data interpretation": "DATA_INTERPRETATION",
    "english": "ENGLISH",
    "general awareness": "GENERAL_AWARENESS",
    "general knowledge": "GENERAL_AWARENESS",
    "banking": "GENERAL_AWARENESS",
    "economy": "GENERAL_AWARENESS",
    "computer": "COMPUTER",
}


# --- per-family position-based subject segmentation ------------------------
# (paper_format, exam_label, stage_label): list of (subject, question_count)
# Order must sum to the paper's question count. Used when section_hint is
# missing (SSC/RRB don't populate it reliably from layout).

_FAMILY_LAYOUTS: Dict[Tuple[str, str, str], List[Tuple[Subject, int]]] = {
    # SSC CGL Tier 1: Reasoning 25, GA 25, Quant 25, English 25 (by section number, not by question number)
    ("SSC_OFFICIAL", "CGL", "TIER-1"): [
        ("REASONING", 25), ("GENERAL_AWARENESS", 25),
        ("QUANT", 25), ("ENGLISH", 25),
    ],
    ("SSC_OFFICIAL", "CHSL", "TIER-1"): [
        ("ENGLISH", 25), ("GENERAL_AWARENESS", 25),
        ("QUANT", 25), ("REASONING", 25),
    ],
    # RRB NTPC CBT 1: GA 40, Maths 30, Reasoning 30 — but the prepp.in PDFs
    # often interleave; fall back to keyword-based subject detection.
    ("RRB_PREPP", "NTPC", "CBT-1"): [],
    # Adda247 papers follow section directions per paper — rely on keyword fallback.
}


# --- topic rules (keyword-based) -------------------------------------------
# Match order matters: earlier rules win. Keywords are matched case-insensitively
# against the concatenated stem + options. All keyword strings are matched as
# substrings (not whole-word) so e.g. "profit" hits "profit-and-loss" queries.

_TOPIC_RULES: Dict[Subject, List[Tuple[Topic, List[str]]]] = {
    "REASONING": [
        ("coding_decoding", ["coded", "coding", "decoded", "decoding", "related to", "in a certain code"]),
        ("series_letter_number", ["letter-number cluster", "letter number", "in the given series"]),
        ("blood_relations", ["brother", "sister", "father", "mother", "uncle", "aunt", "nephew", "grandfather"]),
        ("direction_sense", ["north", "south", "east", "west", "facing", "direction"]),
        ("seating_arrangement_circular", ["circular table", "around a", "facing the centre", "around the table"]),
        ("seating_arrangement_linear", ["two parallel rows", "row 1", "row 2", "linear row", "seated in a row"]),
        ("puzzle_floor", ["floor", "ground floor", "topmost floor"]),
        ("puzzle_box_based", ["boxes are placed", "stack of boxes", "boxes one above"]),
        ("puzzle_month_day", ["on different days", "january, february", "monday, tuesday"]),
        ("syllogism", ["all", "some", "no ", "conclusions"]),
        ("inequality", ["≥", "≤", ">=", "<=", "greater than", "less than"]),
        ("data_sufficiency", ["data provided", "statements are sufficient", "statement i", "statement ii"]),
        ("analogy", ["is related to", "analogous to"]),
        ("odd_one_out", ["odd one out", "does not belong", "three of the following four"]),
        ("mirror_water_image", ["mirror image", "water image"]),
        ("paper_folding", ["paper folding", "cut paper", "punched"]),
        ("dice_cube", ["dice", "cube", "opposite face"]),
        ("venn_diagram", ["venn", "diagram that best represents"]),
        ("statement_conclusion", ["conclusions follow", "assumption"]),
    ],
    "QUANT": [
        ("simplification", ["simplify", "value of", "come in place of the question mark", "? in"]),
        ("number_system", ["divisible by", "remainder", "lcm", "hcf", "prime"]),
        ("percentage", ["percent", "%", "percentage"]),
        ("profit_loss_discount", ["profit", "loss", "discount", "marked price", "cost price", "selling price"]),
        ("simple_compound_interest", ["simple interest", "compound interest", "per annum"]),
        ("ratio_proportion", ["ratio", "proportional", "in the ratio", "third proportional"]),
        ("average", ["average"]),
        ("time_speed_distance", ["speed", "distance", "travels", "km/h", "kmph"]),
        ("time_and_work", ["can do a work", "days to complete", "efficiency", "work together"]),
        ("pipes_and_cisterns", ["pipe", "cistern", "tank", "inlet", "outlet"]),
        ("boats_and_streams", ["boat", "stream", "upstream", "downstream"]),
        ("mixtures_alligation", ["mixture", "alligation"]),
        ("partnership", ["invested", "partnership", "profit shared"]),
        ("mensuration_2d", ["area", "perimeter", "triangle", "quadrilateral", "circle", "circumference"]),
        ("mensuration_3d", ["volume", "surface area", "cylinder", "cone", "sphere", "cuboid"]),
        ("geometry_lines_angles", ["angle", "parallel lines", "transversal", "vertically opposite"]),
        ("trigonometry", ["sin", "cos", "tan", "cot", "sec", "cosec", "sin θ", "sinθ"]),
        ("algebra_equations", ["x^2", "equation", "quadratic"]),
        ("number_series", ["in the given series", "what should come in place", "series"]),
        ("probability", ["probability"]),
        ("permutation_combination", ["ways", "arranged", "permutation", "combination"]),
    ],
    "DATA_INTERPRETATION": [
        ("bar_chart", ["bar graph", "bar chart"]),
        ("line_chart", ["line graph", "line chart"]),
        ("pie_chart", ["pie chart", "pie graph"]),
        ("table", ["the given table", "table shows", "following table"]),
        ("caselet", ["paragraph", "caselet"]),
        ("mixed_graph", ["two graphs", "following graphs"]),
    ],
    "ENGLISH": [
        ("cloze_test", ["select the most appropriate option to fill", "fill in the blank"]),
        ("reading_comprehension", ["read the passage", "according to the passage", "following passage"]),
        ("synonym_antonym", ["synonym", "antonym", "similar meaning", "opposite meaning"]),
        ("spotting_error", ["spot the error", "find the error", "grammatically incorrect"]),
        ("sentence_improvement", ["substitute the highlighted", "improve the sentence", "replacement"]),
        ("idioms_phrases", ["idiom", "meaning of the phrase"]),
        ("one_word_substitution", ["one word substitute", "one word for"]),
        ("para_jumbles", ["rearrange", "correct sequence of sentences"]),
        ("active_passive", ["active voice", "passive voice"]),
        ("direct_indirect", ["indirect speech", "direct speech"]),
        ("spelling", ["correctly spelt", "correctly spelled", "misspelt"]),
        ("fill_preposition", ["fill in the blank with", "fill in the blanks"]),
    ],
    "GENERAL_AWARENESS": [
        ("polity_constitution", ["article", "amendment", "constitution", "directive principles", "fundamental right", "fundamental duty", "parliament", "lok sabha", "rajya sabha"]),
        ("modern_history", ["satyagraha", "non-cooperation", "quit india", "independence", "congress", "mahatma gandhi", "tilak", "patel", "nehru"]),
        ("medieval_history", ["mughal", "sultan", "delhi sultanate", "mansabdari", "aurangzeb", "akbar", "shivaji"]),
        ("ancient_history", ["harappa", "indus valley", "vedic", "gupta", "mauryan", "ashoka", "chandragupta"]),
        ("geography_india", ["himalaya", "ganga", "brahmaputra", "monsoon", "tropic of cancer", "western ghats"]),
        ("geography_world", ["continent", "equator", "tropic", "longitude", "latitude"]),
        ("economy", ["gdp", "inflation", "fiscal", "monetary policy", "reserve bank", "npa"]),
        ("banking_static", ["basel", "nabard", "sebi", "repo rate", "rbi governor", "slr", "crr"]),
        ("awards_books", ["nobel prize", "bharat ratna", "padma vibhushan", "booker", "magsaysay", "author of"]),
        ("science_physics", ["newton", "ohm's law", "pascal", "optics", "refractive"]),
        ("science_chemistry", ["element", "compound", "oxidation", "atomic number", "periodic table"]),
        ("science_biology", ["photosynthesis", "vitamin", "enzyme", "mitochondria", "nephron"]),
        ("sports", ["olympics", "world cup", "cricket", "hockey", "football", "tennis", "badminton"]),
        ("culture", ["classical dance", "kathak", "bharatnatyam", "festival", "unesco"]),
        ("organizations", ["united nations", "world bank", "imf", "wto", "asean", "saarc"]),
    ],
    "COMPUTER": [
        ("fundamentals", ["cpu", "ram", "rom", "operating system", "binary"]),
        ("applications", ["spreadsheet", "word processing", "presentation", "browser"]),
        ("networking", ["osi", "tcp", "ip", "lan", "wan", "protocol"]),
        ("shortcuts", ["shortcut key", "ctrl+", "alt+"]),
    ],
}


@dataclass
class ClassifiedQuestion:
    source_pdf: str
    order: int
    subject: Subject
    topic: Topic
    difficulty_guess: str         # "EASY" | "MEDIUM" | "HARD" — coarse heuristic
    stem_preview: str
    has_correct_answer: bool
    issues: List[str]


def _section_to_subject(section_hint: Optional[str]) -> Optional[Subject]:
    if not section_hint:
        return None
    low = section_hint.lower()
    for kw, canon in _SUBJECT_CANON.items():
        if kw in low:
            return canon
    return None


def _subject_by_layout(
    family: str, exam: str, stage: str, order: int
) -> Optional[Subject]:
    layout = _FAMILY_LAYOUTS.get((family, exam.upper(), stage.upper()))
    if not layout:
        return None
    cursor = 0
    for subject, count in layout:
        if cursor < order <= cursor + count:
            return subject
        cursor += count
    return None


def _subject_by_keywords(text: str) -> Subject:
    """Last-resort keyword fallback — used when neither the section_hint nor
    the paper-layout map resolves a subject.
    """
    t = text.lower()
    # Data interpretation cues often co-exist with quant — detect DI first.
    di_hits = sum(1 for kw in ("bar graph", "pie chart", "line graph", "the given table", "following table") if kw in t)
    if di_hits:
        return "DATA_INTERPRETATION"
    quant_hits = sum(1 for kw in ("simplify", "percent", "ratio", "average", "discount", "speed", "volume", "area", "probability") if kw in t)
    reasoning_hits = sum(1 for kw in ("coding", "syllog", "blood relation", "direction", "arrangement", "puzzle", "analog") if kw in t)
    eng_hits = sum(1 for kw in ("passage", "synonym", "antonym", "idiom", "cloze", "fill in the blank", "sentence") if kw in t)
    ga_hits = sum(1 for kw in ("constitution", "article", "satyagraha", "mughal", "ashoka", "olympic", "rbi", "gdp") if kw in t)
    comp_hits = sum(1 for kw in ("operating system", "cpu", "ram", "ctrl+", "osi") if kw in t)
    scores = {
        "QUANT": quant_hits,
        "REASONING": reasoning_hits,
        "ENGLISH": eng_hits,
        "GENERAL_AWARENESS": ga_hits,
        "COMPUTER": comp_hits,
    }
    best = max(scores, key=lambda k: scores[k])
    return best if scores[best] > 0 else "UNCLASSIFIED"


def classify_subject(
    q: ParsedQuestion, family: str, exam_label: str, stage_label: str
) -> Subject:
    """Resolve a subject label for one parsed question using, in order:

    1. ``section_hint`` mapping — deterministic when the parser captured it.
    2. Per-family layout map — position-based bucket for SSC/RRB papers.
    3. Keyword fallback — best-effort over stem + options text.
    """
    by_hint = _section_to_subject(q.section_hint)
    if by_hint:
        return by_hint
    by_layout = _subject_by_layout(family, exam_label, stage_label, q.order)
    if by_layout:
        return by_layout
    body = q.stem + " " + " ".join(q.options)
    return _subject_by_keywords(body)


def classify_topic(subject: Subject, q: ParsedQuestion) -> Topic:
    """Match the first keyword rule for the given subject. Returns
    ``"UNCLASSIFIED"`` if nothing matches — those Qs should be surfaced for
    admin review rather than silently bucketed somewhere wrong.
    """
    rules = _TOPIC_RULES.get(subject, [])
    text = (q.stem + " " + " ".join(q.options)).lower()
    for topic, keywords in rules:
        if any(kw.lower() in text for kw in keywords):
            return topic
    return "UNCLASSIFIED"


def guess_difficulty(q: ParsedQuestion) -> str:
    """Very coarse difficulty heuristic based on stem length + numeric density.

    Real difficulty requires human judgment; this is a first-pass label so the
    topic-frequency table can at least split easy/medium/hard counts.
    """
    n = len(q.stem)
    digits = sum(1 for ch in q.stem if ch.isdigit())
    if n < 80 and digits < 4:
        return "EASY"
    if n > 220 or digits > 12:
        return "HARD"
    return "MEDIUM"


def classify_paper(
    paper: ParsedPaper, exam_label: str, stage_label: str
) -> List[ClassifiedQuestion]:
    """Classify every question in a paper; returns a flat list so the
    aggregator can group as it likes.
    """
    out: List[ClassifiedQuestion] = []
    for q in paper.questions:
        subject = classify_subject(q, paper.source_format, exam_label, stage_label)
        topic = classify_topic(subject, q) if subject != "UNCLASSIFIED" else "UNCLASSIFIED"
        out.append(
            ClassifiedQuestion(
                source_pdf=paper.pdf_path,
                order=q.order,
                subject=subject,
                topic=topic,
                difficulty_guess=guess_difficulty(q),
                stem_preview=q.stem[:180],
                has_correct_answer=q.correct_index is not None,
                issues=list(q.issues),
            )
        )
    return out
