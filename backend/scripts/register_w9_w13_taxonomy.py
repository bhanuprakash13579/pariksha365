"""
Register all W9-W13 topic_codes into subject_taxonomy.
Each W-batch code that is missing gets a new row pointing to the same
subject/topic as its canonical base code, so the weak-topic system
can map quiz_questions → subject_taxonomy correctly.
"""

import psycopg2, json, re, uuid
from pathlib import Path

SEED_ROOT = Path(__file__).parents[1] / 'seeds' / 'static_gk'

with open(Path(__file__).parents[1] / '.env.local') as f:
    for line in f:
        line = line.strip()
        if line.startswith('PRODUCTION_DB_URL='):
            DB_URL = line.split('=', 1)[1].strip().strip('"').strip("'")
            break

# ── canonical map: prefix → existing taxonomy topic_code ──────────────────
# Keys must be exact prefix of the W-batch topic_code (longest match wins).
# Values MUST exist in subject_taxonomy.
MANUAL: dict[str, str] = {
    # ── English ──────────────────────────────────────────────────────────
    'ENG_ACTIVE_PASSIVE':           'ENG_ACTIVE_PASSIVE_MIXED',
    'ENG_ARTICLES_PREPOSITIONS':    'ENG_PREPOSITIONS_MIXED',
    'ENG_ANTONYMS':                 'ENG_ANTONYMS',
    'ENG_CLOZE_TEST':               'ENG_CLOZE_MIXED',
    'ENG_COMPREHENSION':            'ENG_READING_COMPREHENSION',
    'ENG_DIRECT_INDIRECT':          'ENG_DIRECT_INDIRECT_SPEECH_MIXED',
    'ENG_DOUBLE_BLANKS':            'ENG_FILL_BLANKS_MIXED',
    'ENG_ERROR_DETECTION':          'ENG_ERROR_SPOTTING_MIXED',
    'ENG_FILL_BLANKS_ADV':          'ENG_FILL_BLANKS_MIXED',
    'ENG_FILL_BLANKS_DOUBLE':       'ENG_FILL_BLANKS_MIXED',
    'ENG_FILL_BLANKS_SINGLE':       'ENG_FILL_BLANKS_MIXED',
    'ENG_FILL_BLANKS':              'ENG_FILL_BLANKS_MIXED',
    'ENG_FILL_IN_BLANKS':           'ENG_FILL_BLANKS_MIXED',
    'ENG_GRAMMAR_ADVANCED':         'ENG_GRAMMAR',
    'ENG_GRAMMAR_USAGE':            'ENG_GRAMMAR',
    'ENG_IDIOMS_IN_CONTEXT':        'ENG_IDIOMS_MIXED',
    'ENG_IDIOMS_PHRASES':           'ENG_IDIOMS_MIXED',
    'ENG_NARRATION_ADVANCED':       'ENG_NARRATION_MIXED',
    'ENG_ODD_SENTENCE':             'ENG_ODD_SENTENCE',
    'ENG_ONE_WORD_SUBS_CONTEXT':    'ENG_ONE_WORD_SUBSTITUTION_MIXED',
    'ENG_ONE_WORD_SUBSTITUTION':    'ENG_ONE_WORD_SUBSTITUTION_MIXED',
    'ENG_ONE_WORD':                 'ENG_ONE_WORD_SUBSTITUTION_MIXED',
    'ENG_PARA_COMPLETION':          'ENG_PARA_COMPLETE',
    'ENG_PARA_JUMBLES':             'ENG_PARA_JUMBLES_MIXED',
    'ENG_PHRASE_REPLACEMENT':       'ENG_SENTENCE_IMPROVEMENT_MIXED',
    'ENG_READING_COMP':             'ENG_READING_COMPREHENSION',
    'ENG_REPORTED_SPEECH':          'ENG_NARRATION_REPORTED_SPEECH_MIXED',
    'ENG_SENTENCE_COMPLETION':      'ENG_SENT_COMPLETE',
    'ENG_SENTENCE_IMPROVEMENT':     'ENG_SENTENCE_IMPROVEMENT_MIXED',
    'ENG_SENTENCE_REARRANGEMENT':   'ENG_PARA_JUMBLES_MIXED',
    'ENG_SPELLING':                 'ENG_SPELLING_MIXED',
    'ENG_SPOTTING_ERRORS':          'ENG_ERROR_SPOTTING_MIXED',
    'ENG_SYNONYMS':                 'ENG_SYNONYMS',
    'ENG_TENSES_ADVANCED':          'ENG_TENSES',
    'ENG_VOCABULARY_CONTEXT':       'VOCAB_CONTEXT',
    'ENG_WORD_IN_CONTEXT':          'ENG_GRAMMAR',
    'ENG_WORD_USAGE':               'ENG_GRAMMAR',
    # ── Quantitative Aptitude ─────────────────────────────────────────────
    'QA_AGES':                      'QA_AGES',
    'QA_ALGEBRA_LINEAR_EQ':         'QA_ALGEBRA',
    'QA_ALGEBRA':                   'QA_ALGEBRA',
    'QA_ALLIGATION':                'QA_MIXTURE',
    'QA_AP_GP':                     'QA_NUMBER',
    'QA_AVERAGE':                   'QA_AVERAGE',
    'QA_BOATS_STREAMS':             'QA_BOATS',
    'QA_BOATS':                     'QA_BOATS',
    'QA_CALENDARS':                 'RSN_CLOCK_CALENDAR',
    'QA_CI':                        'QA_CI',
    'QA_CLOCK_PROBLEMS':            'RSN_CLOCK_CALENDAR',
    'QA_CLOCKS_CALENDARS':          'RSN_CLOCK_CALENDAR',
    'QA_CLOCKS':                    'RSN_CLOCK_CALENDAR',
    'QA_COMPOUND_INTEREST':         'QA_CI',
    'QA_COORDINATE_GEOM':           'QA_COORD_GEOM',
    'QA_COORDINATE_GEOMETRY':       'QA_COORD_GEOM',
    'QA_COORDINATE':                'QA_COORD_GEOM',
    'QA_DATA_INTERPRETATION':       'QA_DI',
    'QA_DATA':                      'QA_DI',
    'QA_DISCOUNT_MARKED':           'QA_DISCOUNT',
    'QA_DISCOUNT':                  'QA_DISCOUNT',
    'QA_GEOMETRY_CIRCLES':          'QA_GEOM_CIRCLES',
    'QA_GEOMETRY_TRIANGLES':        'QA_GEOM_TRIANGLES',
    'QA_GEOMETRY':                  'QA_GEOM_TRIANGLES',
    'QA_HEIGHTS_DISTANCES':         'QA_HEIGHTS',
    'QA_LCM_HCF':                   'QA_HCF_LCM',
    'QA_MENSURATION_ADV':           'QA_MENSURATION',
    'QA_MENSURATION':               'QA_MENSURATION',
    'QA_MIXTURE':                   'QA_MIXTURE',
    'QA_NUMBER':                    'QA_NUMBER',
    'QA_PARTNERSHIP':               'QA_PARTNERSHIP',
    'QA_PERCENTAGE_APPLICATIONS':   'QA_PERCENT',
    'QA_PERCENTAGE':                'QA_PERCENT',
    'QA_PERCENT':                   'QA_PERCENT',
    'QA_PERMUTATION_COMBINATION':   'QA_PNC',
    'QA_PERMUTATION':               'QA_PNC',
    'QA_PIPES':                     'QA_PIPES',
    'QA_PROBABILITY':               'QA_PROBABILITY',
    'QA_PROBLEMS_AGES':             'QA_AGES',
    'QA_PROFIT_LOSS_ADV':           'QA_PROFIT_LOSS',
    'QA_PROFIT':                    'QA_PROFIT_LOSS',
    'QA_QUADRATIC_EQUATIONS':       'QA_QUADRATIC',
    'QA_RACES_GAMES':               'QA_RACES',
    'QA_RATIO':                     'QA_RATIO',
    'QA_SHORTCUTS_TRICKS':          'QA_SIMPLIFY',
    'QA_SHORTCUTS':                 'QA_SIMPLIFY',
    'QA_SI':                        'QA_SI',
    'QA_SI_CI':                     'QA_CI',
    'QA_SPEED_DISTANCE_ADV':        'QA_TSD',
    'QA_SPEED_DISTANCE_TIME':       'QA_TSD',
    'QA_SPEED_DISTANCE':            'QA_TSD',
    'QA_SPEED_TIME_DISTANCE':       'QA_TSD',
    'QA_STATISTICS_MEAN_MEDIAN':    'QA_AVERAGE',
    'QA_STATISTICS':                'QA_AVERAGE',
    'QA_SURDS_INDICES':             'QA_NUMBER_SYS',
    'QA_SURDS':                     'QA_NUMBER_SYS',
    'QA_TIME_DISTANCE':             'QA_TSD',
    'QA_TIME_SPEED':                'QA_TSD',
    'QA_TRAINS':                    'QA_TRAINS',
    'QA_TRIGONOMETRY':              'QA_TRIGONOMETRY',
    'QA_WORK_TIME':                 'QA_TIME_WORK',
    'QA_WORK':                      'QA_TIME_WORK',
    # ── Reasoning ────────────────────────────────────────────────────────
    'RSN_ALPHA_NUMERIC':            'RSN_SERIES_LN',
    'RSN_ALPHA_SERIES':             'RSN_ALPHABET',
    'RSN_ALPHANUMERIC_SERIES':      'RSN_SERIES_LN',
    'RSN_ANALOGY':                  'RSN_ANALOGY',
    'RSN_BLOOD_RELATIONS_ADV':      'RSN_BLOOD',
    'RSN_BLOOD_RELATIONS':          'RSN_BLOOD',
    'RSN_BLOOD_REL':                'RSN_BLOOD',
    'RSN_CALENDAR_DAYS':            'RSN_CLOCK_CALENDAR',
    'RSN_CALENDAR':                 'RSN_CLOCK_CALENDAR',
    'RSN_CAUSE_EFFECT':             'RSN_CAUSE_EFFECT',
    'RSN_CLASSIFICATION':           'RSN_CLASSIFICATION',
    'RSN_CODED_BLOOD':              'RSN_BLOOD',
    'RSN_CODED_INEQUALITY':         'RSN_INEQUALITIES',
    'RSN_CODING_DECODING':          'RSN_CODING',
    'RSN_CRITICAL_REASONING':       'RSN_CONCLUSIONS',
    'RSN_CUBES_DICE':               'RSN_DICE_CUBES',
    'RSN_DATA_SUFFICIENCY':         'RSN_DATA_SUFF',
    'RSN_DAY_PERSON_PUZZLE':        'RSN_PUZZLES',
    'RSN_DIRECTION':                'RSN_DIRECTION',
    'RSN_FLOOR_PUZZLE':             'RSN_PUZZLES',
    'RSN_INPUT_OUTPUT_ADV':         'RSN_INPUT_OUTPUT',
    'RSN_INPUT_OUTPUT':             'RSN_INPUT_OUTPUT',
    'RSN_LETTER_SERIES':            'RSN_SERIES_LN',
    'RSN_LOGICAL_DEDUCTION':        'REAS_LOGICAL_DEDUCTION_MIXED',
    'RSN_LOGICAL_SEQUENCE':         'RSN_SERIES',
    'RSN_LOGICAL_VENN':             'RSN_VENN',
    'RSN_MATHEMATICAL_OPERATIONS':  'RSN_MATH_OPS',
    'RSN_MATRIX':                   'RSN_MATRIX',
    'RSN_MIRROR_IMAGE':             'RSN_IMAGES',
    'RSN_MISSING_NUMBER':           'RSN_NUMBER_PUZZLE',
    'RSN_NUMBER_ANALOGY':           'RSN_ANALOGY',
    'RSN_NUMBER_SERIES':            'RSN_SERIES',
    'RSN_ORDERING_RANKING':         'RSN_RANKING',
    'RSN_ORDER_RANKING':            'RSN_RANKING',
    'RSN_ORDER_RANK':               'RSN_RANKING',
    'RSN_PUZZLE_MIXED':             'RSN_PUZZLES',
    'RSN_PUZZLE_SETS':              'RSN_PUZZLES',
    'RSN_RANKING_ORDER':            'RSN_RANKING',
    'RSN_SEATING_ARRANGEMENT':      'RSN_SEATING',
    'RSN_SERIES_COMPLETION':        'RSN_SERIES',
    'RSN_SITTING_ARRANGEMENT':      'RSN_SEATING',
    'RSN_STATEMENT_ASSUMPTIONS':    'RSN_STMT_ASSUMPTION',
    'RSN_STATEMENT_CONCLUSION':     'RSN_CONCLUSIONS',
    'RSN_STATEMENT_CONCLUSIONS':    'RSN_CONCLUSIONS',
    'RSN_SYLLOGISM_ADV':            'RSN_SYLLOGISM',
    'RSN_SYLLOGISM':                'RSN_SYLLOGISM',
    'RSN_VENN':                     'RSN_VENN',
    # ── Vocabulary ────────────────────────────────────────────────────────
    'VOCAB_ANALOGY_ADV':            'VOCAB_SYN_ANT',
    'VOCAB_ANTONYMS_ADV':           'VOCAB_ANTONYMS_MIXED',
    'VOCAB_ANTONYMS_ADVANCED':      'VOCAB_ANTONYMS_MIXED',
    'VOCAB_ANTONYMS_IN_CONTEXT':    'VOCAB_ANTONYMS_MIXED',
    'VOCAB_ANTONYMS_SET3':          'VOCAB_ANTONYMS_MIXED',
    'VOCAB_ANTONYMS_SYNONYMS_MIXED': 'VOCAB_SYN_ANT',
    'VOCAB_ANTONYMS_III':           'VOCAB_ANTONYMS_MIXED',
    'VOCAB_ANTONYMS':               'VOCAB_ANTONYMS_MIXED',
    'VOCAB_COLLOCATIONS':           'VOCAB_THEMATIC',
    'VOCAB_CONFUSABLE_PAIRS':       'VOCAB_CONFUSED_PAIRS_MIXED',
    'VOCAB_DIFFICULT_WORDS':        'VOCAB_HIGH_HIT_SYNONYMS',
    'VOCAB_FILL_BLANKS_VOCAB':      'VOCAB_CONTEXT',
    'VOCAB_FILL_IN_BLANKS':         'ENG_FILL_BLANKS_MIXED',
    'VOCAB_FILL_BLANKS':            'VOCAB_CONTEXT',
    'VOCAB_FOREIGN_PHRASES':        'VOCAB_FOREIGN_PHRASES',
    'VOCAB_FOREIGN_WORDS':          'VOCAB_FOREIGN_WORDS_II_MIXED',
    'VOCAB_FORMAL_INFORMAL':        'VOCAB_CONTEXT',
    'VOCAB_HOMONYMS':               'VOCAB_HOMOPHONES_MIXED',
    'VOCAB_HOMOPHONES':             'VOCAB_HOMOPHONES_MIXED',
    'VOCAB_IDIOMS_ANIMAL':          'VOCAB_IDIOMS',
    'VOCAB_IDIOMS_BODY_PARTS':      'VOCAB_IDIOMS_MIXED_TIERS',
    'VOCAB_IDIOMS_ORIGIN':          'VOCAB_IDIOMS_MIXED_TIERS',
    'VOCAB_IDIOMS_PHRASES':         'VOCAB_IDIOMS',
    'VOCAB_MEDICAL_LEGAL':          'VOCAB_MEDICAL_HEALTH_MIXED',
    'VOCAB_ONE_WORD_SUBS':          'VOCAB_OWS',
    'VOCAB_ONE_WORD':               'VOCAB_OWS',
    'VOCAB_PHOBIA_MANIA':           'VOCAB_OWS',
    'VOCAB_PHRASAL_VERBS':          'VOCAB_PHRASAL',
    'VOCAB_PHRASES_LITERATURE':     'VOCAB_LITERATURE_TERMS_MIXED',
    'VOCAB_PREFIXES_SUFFIXES':      'VOCAB_PREFIXES_MIXED',
    'VOCAB_PROVERBS_CONTEXT':       'VOCAB_PROVERBS_MIXED',
    'VOCAB_PROVERBS_III':           'VOCAB_PROVERBS_MIXED',
    'VOCAB_PROVERBS':               'VOCAB_PROVERBS_MIXED',
    'VOCAB_ROOT_WORDS_III':         'VOCAB_WORD_ROOTS',
    'VOCAB_ROOT_WORDS':             'VOCAB_WORD_ROOTS',
    'VOCAB_ROOTS_III':              'VOCAB_WORD_ROOTS',
    'VOCAB_ROOTS':                  'VOCAB_WORD_ROOTS',
    'VOCAB_SPELLING_CORRECTION':    'ENG_SPELLING_MIXED',
    'VOCAB_SYNONYMS_ADV':           'VOCAB_SYNONYMS_ADVANCED_MIXED',
    'VOCAB_SYNONYMS_CONTEXT':       'VOCAB_SYNONYMS_MIXED',
    'VOCAB_SYNONYMS_IN_CONTEXT':    'VOCAB_SYNONYMS_MIXED',
    'VOCAB_SYNONYMS_IV':            'VOCAB_SYNONYMS_MIXED',
    'VOCAB_SYNONYMS':               'VOCAB_SYNONYMS_MIXED',
    'VOCAB_WORD_FORMATION':         'VOCAB_PREFIXES_MIXED',
    'VOCAB_WORD_FORMS':             'VOCAB_CONTEXT',
    'VOCAB_WORD_PAIRS_III':         'VOCAB_CONFUSED_PAIRS_MIXED',
    'VOCAB_WORD_PAIRS':             'VOCAB_CONFUSED_PAIRS_MIXED',
    'VOCAB_WORD_USAGE':             'VOCAB_CONTEXT_MEANING',
}


def load_taxonomy(cur) -> dict:
    cur.execute('SELECT topic_code, topic, subject FROM subject_taxonomy')
    return {r[0]: (r[1], r[2]) for r in cur.fetchall()}


def find_canonical(tc: str, taxonomy: dict) -> tuple | None:
    # 1. Strip W-suffix → check taxonomy directly
    base = re.sub(r'_W\d+(_B\d+)?$', '', tc)
    if base in taxonomy:
        return taxonomy[base]

    # 2. Longest MANUAL prefix match
    best_canon = None
    best_len = 0
    for prefix, canon_code in MANUAL.items():
        if tc.startswith(prefix) and len(prefix) > best_len:
            if canon_code in taxonomy:
                best_canon = taxonomy[canon_code]
                best_len = len(prefix)
    return best_canon


def collect_missing(taxonomy: dict) -> dict[str, tuple]:
    """Returns {topic_code: (subject, topic)} for W9-W13 codes not in taxonomy."""
    missing = {}
    for f in sorted(SEED_ROOT.rglob('*.json')):
        try:
            d = json.loads(f.read_text())
        except Exception:
            continue
        tc = d.get('topic_code', '')
        if not re.search(r'_W(9|10|11|12|13)', tc):
            continue
        if tc in taxonomy:
            continue
        missing[tc] = (d.get('subject', ''), d.get('topic', tc))
    return missing


def main():
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    taxonomy = load_taxonomy(cur)

    missing = collect_missing(taxonomy)
    print(f'Missing from taxonomy: {len(missing)}')

    to_insert = []
    still_unresolved = []

    for tc, (seed_subject, seed_topic) in sorted(missing.items()):
        canon = find_canonical(tc, taxonomy)
        if canon:
            _canon_topic, canon_subject = canon
            # Use the seed file's own topic (already unique per file).
            # Use canonical subject for consistency with the taxonomy family.
            to_insert.append((tc, seed_topic, canon_subject))
        else:
            still_unresolved.append(tc)

    print(f'Will INSERT: {len(to_insert)}')
    print(f'Still unresolved: {len(still_unresolved)}')
    for tc in still_unresolved:
        print(f'  UNRESOLVED: {tc}')

    if still_unresolved:
        print('\nAborting — fix unresolved codes first.')
        return

    # DRY-RUN first
    print('\n--- DRY RUN (first 10 rows) ---')
    for tc, topic, subject in to_insert[:10]:
        print(f'  INSERT topic_code={tc!r}  subject={subject!r}')

    confirm = input(f'\nInsert {len(to_insert)} rows into subject_taxonomy? [y/N] ').strip().lower()
    if confirm != 'y':
        print('Aborted.')
        return

    inserted = 0
    for tc, topic, subject in to_insert:
        row_id = str(uuid.uuid5(uuid.UUID('11111111-0000-0000-0000-000000000005'), tc))
        cur.execute(
            """
            INSERT INTO subject_taxonomy (id, topic_code, topic, subject, aliases, created_at)
            VALUES (%s, %s, %s, %s, '[]'::jsonb, NOW())
            ON CONFLICT (topic_code) DO NOTHING
            """,
            (row_id, tc, topic, subject)
        )
        inserted += cur.rowcount

    conn.commit()
    print(f'\nInserted {inserted} new taxonomy rows.')

    # Verify
    cur.execute('SELECT COUNT(*) FROM subject_taxonomy')
    print(f'subject_taxonomy total rows now: {cur.fetchone()[0]}')


if __name__ == '__main__':
    main()
