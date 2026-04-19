"""Canonical topic → short-code mapping used as the deterministic join key in
the weak-topic matcher.

Codes are intentionally short and stable: ``QNT_PCT`` is easier for admins to
recognise in the DB than a 40-char topic string, and it gives the classifier a
fixed identity even if the human-readable topic label changes. Treat this file
as **append-only** — renaming or removing a code will orphan every quiz
question tagged with the old value. Add new topics below, don't rewrite.
"""
from __future__ import annotations

from typing import Dict, Tuple

# Subject → Topic → (topic_code, pretty_label)
_TOPIC_CODES: Dict[str, Dict[str, Tuple[str, str]]] = {
    "REASONING": {
        "coding_decoding": ("RSN_CODE", "Coding–Decoding"),
        "series_letter_number": ("RSN_SERIES_LN", "Letter/Number Series"),
        "blood_relations": ("RSN_BLOOD", "Blood Relations"),
        "direction_sense": ("RSN_DIR", "Direction Sense"),
        "seating_arrangement_circular": ("RSN_SEAT_CIRC", "Circular Seating"),
        "seating_arrangement_linear": ("RSN_SEAT_LIN", "Linear Seating"),
        "puzzle_floor": ("RSN_PUZ_FLOOR", "Floor Puzzle"),
        "puzzle_box_based": ("RSN_PUZ_BOX", "Box-Based Puzzle"),
        "puzzle_month_day": ("RSN_PUZ_MD", "Month/Day Puzzle"),
        "syllogism": ("RSN_SYL", "Syllogism"),
        "inequality": ("RSN_INEQ", "Inequality"),
        "data_sufficiency": ("RSN_DS", "Data Sufficiency"),
        "analogy": ("RSN_ANA", "Analogy"),
        "odd_one_out": ("RSN_ODD", "Odd One Out"),
        "mirror_water_image": ("RSN_IMG", "Mirror/Water Image"),
        "paper_folding": ("RSN_FOLD", "Paper Folding"),
        "dice_cube": ("RSN_DICE", "Dice/Cube"),
        "venn_diagram": ("RSN_VENN", "Venn Diagram"),
        "statement_conclusion": ("RSN_STMT", "Statement–Conclusion"),
    },
    "QUANT": {
        "simplification": ("QNT_SIMP", "Simplification"),
        "number_system": ("QNT_NUM", "Number System"),
        "percentage": ("QNT_PCT", "Percentage"),
        "profit_loss_discount": ("QNT_PLD", "Profit, Loss & Discount"),
        "simple_compound_interest": ("QNT_SI_CI", "Simple & Compound Interest"),
        "ratio_proportion": ("QNT_RATIO", "Ratio & Proportion"),
        "average": ("QNT_AVG", "Average"),
        "time_speed_distance": ("QNT_TSD", "Time, Speed & Distance"),
        "time_and_work": ("QNT_TW", "Time & Work"),
        "pipes_and_cisterns": ("QNT_PIPES", "Pipes & Cisterns"),
        "boats_and_streams": ("QNT_BOATS", "Boats & Streams"),
        "mixtures_alligation": ("QNT_MIX", "Mixtures & Alligation"),
        "partnership": ("QNT_PART", "Partnership"),
        "mensuration_2d": ("QNT_MENS_2D", "Mensuration (2D)"),
        "mensuration_3d": ("QNT_MENS_3D", "Mensuration (3D)"),
        "geometry_lines_angles": ("QNT_GEOM", "Geometry — Lines & Angles"),
        "trigonometry": ("QNT_TRIG", "Trigonometry"),
        "algebra_equations": ("QNT_ALG", "Algebra"),
        "number_series": ("QNT_NSER", "Number Series"),
        "probability": ("QNT_PROB", "Probability"),
        "permutation_combination": ("QNT_PC", "Permutation & Combination"),
    },
    "DATA_INTERPRETATION": {
        "bar_chart": ("DI_BAR", "Bar Chart"),
        "line_chart": ("DI_LINE", "Line Chart"),
        "pie_chart": ("DI_PIE", "Pie Chart"),
        "table": ("DI_TBL", "Tabular DI"),
        "caselet": ("DI_CASE", "Caselet"),
        "mixed_graph": ("DI_MIXED", "Mixed Graph"),
    },
    "ENGLISH": {
        "cloze_test": ("ENG_CLOZE", "Cloze Test"),
        "reading_comprehension": ("ENG_RC", "Reading Comprehension"),
        "synonym_antonym": ("ENG_SYN", "Synonym/Antonym"),
        "spotting_error": ("ENG_ERR", "Spotting Error"),
        "sentence_improvement": ("ENG_IMPROV", "Sentence Improvement"),
        "idioms_phrases": ("ENG_IDIOM", "Idioms & Phrases"),
        "one_word_substitution": ("ENG_OWS", "One-Word Substitution"),
        "para_jumbles": ("ENG_PARA", "Para Jumbles"),
        "active_passive": ("ENG_VOICE", "Active/Passive Voice"),
        "direct_indirect": ("ENG_SPEECH", "Direct/Indirect Speech"),
        "spelling": ("ENG_SPELL", "Spelling"),
        "fill_preposition": ("ENG_FILL", "Fill in the Blanks"),
    },
    "GENERAL_AWARENESS": {
        "polity_constitution": ("GA_POL", "Polity & Constitution"),
        "modern_history": ("GA_HIS_MOD", "Modern History"),
        "medieval_history": ("GA_HIS_MED", "Medieval History"),
        "ancient_history": ("GA_HIS_ANC", "Ancient History"),
        "geography_india": ("GA_GEO_IN", "Indian Geography"),
        "geography_world": ("GA_GEO_WORLD", "World Geography"),
        "economy": ("GA_ECON", "Economy"),
        "banking_static": ("GA_BANK", "Banking Awareness"),
        "awards_books": ("GA_AWARDS", "Awards & Books"),
        "science_physics": ("GA_SCI_PHY", "Physics"),
        "science_chemistry": ("GA_SCI_CHEM", "Chemistry"),
        "science_biology": ("GA_SCI_BIO", "Biology"),
        "sports": ("GA_SPORTS", "Sports"),
        "culture": ("GA_CULT", "Art & Culture"),
        "organizations": ("GA_ORG", "International Organizations"),
    },
    "COMPUTER": {
        "fundamentals": ("CMP_FUND", "Fundamentals"),
        "applications": ("CMP_APP", "Applications"),
        "networking": ("CMP_NET", "Networking"),
        "shortcuts": ("CMP_SHORT", "Shortcuts"),
    },
}


def get_topic_code(subject: str, topic: str) -> str:
    """Return the canonical code for (subject, topic), or a synthesised
    ``<SUBJECT>_UNC`` fallback so unclassified questions still carry a stable
    key.
    """
    subj_map = _TOPIC_CODES.get(subject)
    if subj_map and topic in subj_map:
        return subj_map[topic][0]
    # Fallback: <SUBJECT_PREFIX>_UNC for "Unclassified" within a known subject,
    # or a very generic GEN_UNC for unknown subjects.
    if subject == "UNCLASSIFIED":
        return "GEN_UNC"
    return f"{subject.split('_')[0][:3].upper()}_UNC"


def get_pretty_topic(subject: str, topic: str) -> str:
    subj_map = _TOPIC_CODES.get(subject)
    if subj_map and topic in subj_map:
        return subj_map[topic][1]
    return topic.replace("_", " ").title() if topic else "Unclassified"
