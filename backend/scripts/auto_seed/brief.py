"""Emit a generation brief for the next-priority topic.

Output (stdout, JSON):
    {
      "topic_code", "subject", "topic", "existing_count",
      "existing_stems": ["already-asked stem 1", ...],
      "rules": {... full gate rules ...},
      "staging_path": "/tmp/auto_seed_staging_<topic>.json",
      "expected_schema": "A | B (both accepted by apply)"
    }

Used by Claude-in-session to compose the next 7-Q bundle without
re-reading the topic's bundle file by hand.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from .canonical import SUBJECT_FOLDER
from .priority import next_picks

_BACKEND = Path(__file__).resolve().parents[2]
_STATE = _BACKEND / "scripts" / "auto_seed" / "state.json"
_POOL = _BACKEND / "seeds" / "static_gk"


_QA_PATTERN_HINTS: dict[str, str] = {
    "QA_PERCENT": "Cover: reverse-%, population growth, election problems, successive %, % of a %, income-expenditure. NOT just 'A is X% more than B'.",
    "QA_PROFIT_LOSS": "Cover: dishonest dealer (false weight), markup-then-discount, cost from profit%, selling below CP, profit on total lot. NOT just 'SP=?, CP=?'.",
    "QA_SI": "Cover: rate find, time find, SI vs amount, equal SI periods, split principal. NOT just SI=PRT/100 plug-in.",
    "QA_CI": "Cover: CI-SI difference formula, half-yearly/quarterly compounding, installment loan, CI on increasing population. NOT just basic P(1+r)^n.",
    "QA_TIME_WORK": "Cover: LCM efficiency, alternate-day work, leaving/joining mid-work, wages split by efficiency, A+B together then alone. NOT just D=W/E plug-in.",
    "QA_TSD": "Cover: relative speed (same/opposite), average speed = 2xy/(x+y), late-early problems, train crossing, circular track meeting. NOT just D=S×T.",
    "QA_PIPES": "Cover: leak + inlet, time to fill with both open, pipe efficiency ratio, tank fill/empty. Use LCM method.",
    "QA_TRAINS": "Cover: train vs pole, train vs platform, two trains same/opposite direction, length-find from crossing time.",
    "QA_SIMPLIFY": "Cover: BODMAS with nested brackets, square/cube roots in expression, surds simplification, approximation to nearest integer.",
    "QA_HCF_LCM": "Cover: HCF×LCM=product, LCM for bells/cycles, HCF of fractions, word problems (largest container, fewest tiles).",
    "QA_TRIGONOMETRY": "Cover: exact values (sin30°,cos60°,tan45°,sin90°), identities (sin²+cos²=1), height-of-tower, complementary angle identity.",
    "QA_MEN_2D": "Cover: area of composite shapes, perimeter word problems, sector/segment, path around rectangle, ratio of areas.",
    "QA_MEN_3D": "Cover: volume of cylinder/cone/sphere, CSA vs TSA, melting and recasting, hemisphere on cylinder, frustum.",
    "QA_COORD_GEOM": "Cover: distance formula, midpoint, section formula, area of triangle with vertices, slope, collinearity check.",
    "QA_NUMBER_SERIES": "Cover: arithmetic series, geometric series, difference-of-differences, prime-based series, alternating series, square/cube series.",
    "QA_APPROX": "Cover: round to nearest 10/100, fraction approximation (√2≈1.41), BODMAS shortcut, estimation without calculator.",
    "QA_SURDS": "Cover: laws of indices (a^m × a^n), rationalization of denominator, (√a + √b)(√a − √b) = a−b, simplify compound surds.",
    "QA_ALGEBRA": "Cover: algebraic identities (a+b)², (a−b)², a³+b³, linear 2-variable system, find value of expression.",
    "QA_PNC": "Cover: arrangements with repetition/without, selections from group, circular permutation n!/n, word arrangements.",
    "QA_QUADRATIC": "Cover: factorization method, sum/product of roots, nature of roots (discriminant), roots of equation.",
    "QA_RACES": "Cover: giving a start in metres, giving a start in time, head start, circular race meeting, beat by X metres.",
    "QA_GEOM_TRIANGLES": "Cover: Pythagoras triples (3-4-5, 5-12-13), similarity ratios, angle bisector theorem, centroid, exterior angle.",
    "QA_MIXTURE": "Cover: alligation rule (cross method), dilution & replacement, mixture of two items at different prices.",
}

_RSN_PATTERN_HINTS: dict[str, str] = {
    "RSN_ANALOGY": "Vary the relationship type across 7 Qs: tool→user, part→whole, word→antonym, number ratio, letter-shift, animal→home, product→raw material.",
    "RSN_SERIES": "Vary across: arithmetic number series, geometric, difference-of-differences, letter series (position shift), alpha-numeric, prime-based, alternating.",
    "RSN_CODING": "Vary: letter coding (shift), number coding, symbol substitution, reverse coding, mixed letter-number coding. Avoid repeating same shift-amount.",
    "RSN_SYLLOGISM": "Cover: All-Some-No combinations, possibility cases (Some A may be B), negative conclusions, Venn diagram approach. Include at least 2 multi-statement syllogisms.",
    "RSN_DIRECTION": "Cover: pure direction sense, shadow direction (morning/evening), coded directions (North=East), distance + direction combined.",
    "RSN_BLOOD": "Cover: generation-tree, 'pointing to photo' format, coded blood relations (P$Q = P is father of Q), gender-unspecified cases.",
    "RSN_SEATING": "Cover: linear single-row, linear double-facing, circular facing-centre, square/rectangular arrangement.",
    "RSN_SEATING_CIRCULAR": "Cover: 8-person circular, some facing out, constraints like 'A is 2nd to right of B', fixed positions.",
    "RSN_SEATING_LINEAR": "Cover: 6-7 persons in a row, 'not adjacent', 'exactly between', double-row facing.",
    "RSN_PUZZLES": "Cover: floor-based puzzle, day/month scheduling, box-stacking, colour-assignment, combination puzzle.",
    "RSN_CLOCK_CALENDAR": "Cover: angle between hands, time gained/lost by fast/slow clock, day of week for a date, leap year calculation, odd days.",
    "RSN_MATRIX": "Cover: complete the matrix (number rule), letter matrix (position pattern), 3×3 with missing value, rule-detection.",
    "RSN_WORD_FORM": "Cover: words formed from letters of given word, meaningful 3-letter words from scrambled letters, anagram identification.",
    "RSN_MISSING_NUM": "Cover: number triangle (sum of corners = centre), number square, magic square, find ? in grid using consistent rule.",
    "RSN_MATH_OPS": "Cover: symbol substitution (+ means ×), balance the equation, verify using substituted operators, BODMAS after substitution.",
    "RSN_STMT_ASSUMPTION": "Cover: implicit assumptions (NOT stated but must be true for statement to make sense), distinguish assumption vs inference vs course-of-action.",
    "RSN_INPUT_OUTPUT": "Cover: word/number shifting rules, step-by-step rearrangement, determine output at step N.",
    "RSN_INEQUALITIES": "Cover: coded inequalities (P > Q ≥ R), find relationship between non-adjacent elements, 'either-or' conclusions.",
    "RSN_CLASSIFICATION": "Cover: find odd one out by category (not random), the link must be non-obvious — size, type, scientific class, function.",
    "RSN_VENN": "Cover: Venn with 3 circles (only-A, only-B, A∩B only, A∩B∩C), word problems (students who like all 3 subjects).",
    "RSN_DATA_SUFF": "Cover: determine if statement I alone, II alone, both needed, or neither is sufficient to answer the question.",
}

_ENG_PATTERN_HINTS: dict[str, str] = {
    "ENG_SYNONYMS": "Cover words from different registers: formal (enumerate/elucidate), literary (melancholy/ephemeral), administrative (promulgate/adjudicate). Options must be 4-7 word phrases like 'to list out carefully'.",
    "ENG_ANTONYMS": "Cover antonyms at B2-C1 level: words frequently misidentified by test-takers. Distractors = plausible near-antonyms students confuse.",
    "ENG_OWS": "Cover: legal/administrative terms, human behaviour words, collective nouns, scientific processes. Mix familiar and niche.",
    "ENG_IDIOMS": "Cover idioms actually used in SSC papers: 'at the drop of a hat', 'a bolt from the blue', 'bite the bullet'. Include meaning AND usage context in explanation.",
    "ENG_CLOZE": "Generate full 4-sentence paragraphs with 2-3 blanks each. Words must fit grammatically AND contextually. Test collocations, not just vocabulary.",
    "ENG_ERROR_SPOT": "Cover: SVA errors, wrong tense sequence, misplaced modifier, wrong preposition, article errors, pronoun-antecedent, double negative.",
    "ENG_SPELLING": "Pick 7 commonly misspelt words at SSC CGL level: accommodate, occurrence, liaison, conscientious, necessary, questionnaire, privilege. Options = 3 misspellings + correct.",
    "ENG_FIB": "Mix single-blank and double-blank questions. Cover: collocations (make/do distinction), preposition choice, verb form, transition words.",
    "ENG_SENTENCE_IMP": "Underline a grammatically wrong phrase; options = 4 rewrites. Cover: dangling participle, wrong verb form, redundancy, wrong idiom.",
    "ENG_PARA_JUMBLES": "Generate 5-6 sentence paragraphs to rearrange. First sentence is always given. Include logical connectors (however, therefore, consequently).",
    "ENG_TENSES": "Cover: simple vs continuous vs perfect, reported speech tense shift, conditional tense (If + past perfect → would have), narrative tense consistency.",
    "ENG_GRAMMAR_VOICE": "Cover active→passive and passive→active for all tenses. Include impersonal passive, double-object passive, and modals (should be done).",
    "ENG_GRAMMAR_NARRATION": "Cover: say vs tell vs ask, time/place expression shifts (now→then, here→there), tense backshift, pronoun change in reporting.",
}

_DEFAULT_HINT = (
    "Prioritise questions that examiners actually set: under-asked angles on "
    "core topics, GI tags, folk arts, niche but PYQ-frequent terminology. Avoid "
    "namesake/trivial stems where the answer is obvious from the question."
)


def _exam_hint_for(subject: str, topic_code: str) -> str:
    if subject == "Quantitative Aptitude":
        return _QA_PATTERN_HINTS.get(topic_code, (
            "For each question pick a DIFFERENT application type of this topic as seen in "
            "SSC CGL/CHSL papers. Each explanation must include a **Short Trick:** section "
            "showing the fastest exam-room calculation method."
        ))
    if subject == "Reasoning":
        return _RSN_PATTERN_HINTS.get(topic_code, (
            "Vary the question pattern type within this reasoning topic. Show step-by-step "
            "logic in explanations. Cover all variants tested in SSC CGL/CHSL."
        ))
    if subject in ("English", "Vocabulary"):
        return _ENG_PATTERN_HINTS.get(topic_code, (
            "Cover different question formats for this English topic as tested in SSC CGL. "
            "State the grammar rule or word-formation principle in every explanation."
        ))
    return _DEFAULT_HINT


def _existing_stems_for(topic_code: str) -> list[str]:
    """Return existing stems for a canonical topic_code.
    Searches both the exact filename AND any question-level topic_code match
    so newly-tagged NOTAG questions are also deduped.
    """
    stems: list[str] = []
    seen_files: set[Path] = set()

    # 1) Exact filename match (fast path for canonical files)
    for f in _POOL.rglob(f"{topic_code}*.json"):
        if f in seen_files:
            continue
        seen_files.add(f)
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        questions = d if isinstance(d, list) else d.get("questions", [])
        for q in questions:
            if not isinstance(q, dict):
                continue
            # Only include if this question is tagged to our canonical code
            q_tc = q.get("topic_code", "")
            if q_tc and q_tc != topic_code:
                continue  # belongs to a different canonical code
            s = q.get("stem") or q.get("text")
            if s:
                stems.append(s)

    # 2) Scan all QRE files for question-level topic_code matches
    # (catches NOTAG-fixed questions in files with non-canonical filenames)
    for folder in ("quant", "quantitative_aptitude", "reasoning", "english", "vocabulary"):
        folder_path = _POOL / folder
        if not folder_path.exists():
            continue
        for f in folder_path.rglob("*.json"):
            if f in seen_files:
                continue
            seen_files.add(f)
            try:
                d = json.loads(f.read_text())
            except Exception:
                continue
            questions = d if isinstance(d, list) else d.get("questions", [])
            for q in questions:
                if not isinstance(q, dict):
                    continue
                if q.get("topic_code") != topic_code:
                    continue
                s = q.get("stem") or q.get("text")
                if s:
                    stems.append(s)

    return stems


def _topic_code_map() -> dict[str, str]:
    try:
        import importlib.util
        _path = Path(__file__).resolve().parents[1] / "topic_code_map.py"
        spec = importlib.util.spec_from_file_location("topic_code_map", _path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(mod)  # type: ignore
        return getattr(mod, "TOPIC_CODE_MAP", {})
    except Exception:
        return {}


def _taxonomy_topic_info(topic_code: str) -> dict | None:
    """Look up subject + topic name for a code that's in taxonomy but not on disk yet."""
    try:
        import importlib.util
        _path = Path(__file__).resolve().parents[2] / "app" / "services" / "taxonomy_data.py"
        spec = importlib.util.spec_from_file_location("taxonomy_data", _path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore
        spec.loader.exec_module(mod)  # type: ignore
        for subj, topic, tc, _ in mod.TAXONOMY_EXPANDED:
            if tc == topic_code:
                return {"subject": subj, "topic": topic}
    except Exception:
        pass
    return None


def make_brief(topic_code: str | None = None, exclude_codes: set[str] | None = None) -> dict:
    state = json.loads(_STATE.read_text())
    tc_map = _topic_code_map()
    # Reverse map: canonical → set of raw codes
    reverse_map: dict[str, list[str]] = {}
    for raw, canon in tc_map.items():
        reverse_map.setdefault(canon, []).append(raw)

    if topic_code:
        pick = None
        # 1) Exact match in state (already canonical)
        for t in state["topics"]:
            if t["topic_code"] == topic_code:
                pick = {
                    "topic_code": topic_code,
                    "subject": t["subject"],
                    "topic": t["topic"],
                    "existing": t["questions"],
                    "high_weight": False,
                }
                break
        # 2) Canonical aggregation: sum questions from all aliased raw codes
        if pick is None:
            total_existing = 0
            subj, top = None, None
            aliased_raws = reverse_map.get(topic_code, [])
            for t in state["topics"]:
                if t["topic_code"] in aliased_raws or tc_map.get(t["topic_code"]) == topic_code:
                    total_existing += t["questions"]
                    if subj is None:
                        subj, top = t["subject"], t.get("topic")
            if subj:
                pick = {"topic_code": topic_code, "subject": subj, "topic": top,
                        "existing": total_existing, "high_weight": False}
        # 3) Brand-new taxonomy topic with no seed files at all
        if pick is None:
            info = _taxonomy_topic_info(topic_code)
            if info:
                pick = {"topic_code": topic_code, "subject": info["subject"],
                        "topic": info["topic"], "existing": 0, "high_weight": False}
        if pick is None:
            return {"error": f"topic_code {topic_code} not in state or taxonomy"}
    else:
        picks = next_picks(state, n=1, exclude=exclude_codes or set())
        if not picks:
            return {"error": "no candidate topics — pool may be saturated"}
        pick = picks[0]

    existing_stems = _existing_stems_for(pick["topic_code"])
    folder = SUBJECT_FOLDER.get(pick["subject"], "general_knowledge")

    return {
        "topic_code": pick["topic_code"],
        "subject": pick["subject"],
        "topic": pick["topic"],
        "high_weight": pick.get("high_weight", False),
        "existing_count": pick["existing"],
        "target": pick.get("target"),
        "deficit": pick.get("deficit"),
        "priority": pick.get("priority"),
        "bundle_path": f"seeds/static_gk/{folder}/{pick['topic_code']}.json",
        "staging_path": f"/tmp/auto_seed_staging_{pick['topic_code']}.json",
        "existing_stems": existing_stems,
        "rules": {
            "questions_per_file": 7,
            "difficulty_shape_options": ["2-easy/3-medium/2-hard", "2-easy/4-medium/1-hard"],
            "difficulty_per_q_strict_order": "Q1-Q2 easy, Q3-Q5 medium, Q6-Q7 hard",
            "options_per_q": 4,
            "option_keys": "A/B/C/D",
            "parity_max_ratio": "len(correct)/min(len(wrong)) < 1.30 — pad SHORT WRONG options, never the correct one",
            "explanation_required": "yes, ≥30 chars; should justify correct AND why tempting wrong is wrong",
            "subject_must_be_canonical": "one of the 14 canonical strings; new files must match existing canonical",
            "schema": "either A (stem/option_text+is_correct/correct_letter, uppercase difficulty) or B (text/key+text/correct, lowercase difficulty) — apply auto-transcodes B→A",
            "must_not_overlap_existing_stems": "see 'existing_stems' list — generate complementary angles, not paraphrases",
            "no_visible_tier_tags": "no [Clerk tier] / [CGL tier] / [Mains] prefixes in stems",
            "no_absolute_language_in_options": "avoid 'always', 'never', 'all of the above', 'none of the above'",
            "no_post_2020_facts": "static answers only; no current affairs or appointment-based facts",
            "exam_relevance": "must be plausibly set by SSC CGL/CHSL/IBPS/SBI/RRB examiner; pick under-asked angles on high-PYQ topics",
        },
        "exam_relevance_hint": _exam_hint_for(pick["subject"], pick["topic_code"]),
    }


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("topic_code", nargs="?", default=None,
                    help="topic_code to brief (default: next-priority pick)")
    ap.add_argument("--json", action="store_true", help="emit raw JSON only")
    args = ap.parse_args()
    brief = make_brief(args.topic_code)
    if args.json:
        print(json.dumps(brief, indent=2, ensure_ascii=False))
        return 0 if "error" not in brief else 1
    if "error" in brief:
        print(f"error: {brief['error']}")
        return 1
    print(f"NEXT PICK: {brief['topic_code']}")
    print(f"  subject: {brief['subject']}  topic: {brief['topic']}")
    print(f"  existing: {brief['existing_count']}  target: {brief['target']}  "
          f"deficit: {brief['deficit']}  priority: {brief['priority']}")
    print(f"  bundle_path: {brief['bundle_path']}")
    print(f"  staging_path: {brief['staging_path']}")
    print(f"  high_weight: {brief['high_weight']}")
    print(f"  existing stems ({len(brief['existing_stems'])}):")
    for s in brief["existing_stems"][:20]:
        print(f"    - {s[:120]}")
    if len(brief["existing_stems"]) > 20:
        print(f"    ... +{len(brief['existing_stems']) - 20} more")
    print()
    print("Rules:")
    for k, v in brief["rules"].items():
        print(f"  • {k}: {v}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
