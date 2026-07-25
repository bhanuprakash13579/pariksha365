"""
Practice Service — Auto-generates quizzes from weak topics using deterministic topic_code matching.
Zero fuzzy logic in the hot path. All matching is exact WHERE topic_code = 'X'.
"""
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import func, case
from app.models.quiz_pool import QuizQuestion, QuizAttempt, UserWeakTopic, UserStreak, UserTopicMastery
from app.models.attempt import Attempt, AttemptStatus
from app.models.user_answer import UserAnswer
from app.models.question import Question
from app.services import taxonomy_service

# Pre-defined quiz categories (for UI display)
QUIZ_CATEGORIES = [
    {"key": "polity", "name": "Polity", "icon": "library-outline", "color": "#8b5cf6"},
    {"key": "history", "name": "History", "icon": "time-outline", "color": "#f59e0b"},
    {"key": "geography", "name": "Geography", "icon": "globe-outline", "color": "#10b981"},
    {"key": "economics", "name": "Economics", "icon": "trending-up-outline", "color": "#3b82f6"},
    {"key": "physics", "name": "Physics", "icon": "flask-outline", "color": "#ef4444"},
    {"key": "chemistry", "name": "Chemistry", "icon": "beaker-outline", "color": "#f97316"},
    {"key": "biology", "name": "Biology", "icon": "leaf-outline", "color": "#22c55e"},
    {"key": "science_technology", "name": "Science & Technology", "icon": "rocket-outline", "color": "#6366f1"},
    {"key": "quantitative_aptitude", "name": "Quantitative Aptitude", "icon": "calculator-outline", "color": "#6366f1"},
    {"key": "reasoning", "name": "Reasoning", "icon": "bulb-outline", "color": "#f97316"},
    {"key": "english", "name": "English", "icon": "language-outline", "color": "#14b8a6"},
    {"key": "vocabulary", "name": "Vocabulary", "icon": "book-outline", "color": "#a855f7"},
    {"key": "computer_knowledge", "name": "Computer Knowledge", "icon": "desktop-outline", "color": "#8b5cf6"},
    {"key": "current_affairs", "name": "Current Affairs", "icon": "newspaper-outline", "color": "#ec4899"},
    {"key": "general_knowledge", "name": "General Knowledge", "icon": "school-outline", "color": "#84cc16"},
]

SUBJECT_KEY_MAP = {cat["key"]: cat["name"] for cat in QUIZ_CATEGORIES}


def _subj_match(value: str):
    """WHERE condition matching QuizQuestion.subject regardless of space vs underscore storage."""
    norm = value.lower().replace("_", " ")
    return func.replace(func.lower(QuizQuestion.subject), "_", " ") == norm


async def get_quiz_categories_with_counts(db: AsyncSession) -> list:
    """Per-category question counts — single round-trip instead of one query
    per category (the old loop made 14 sequential COUNTs, ~14x the latency).
    """
    stmt = (
        select(func.lower(QuizQuestion.subject), func.count(QuizQuestion.id))
        .group_by(func.lower(QuizQuestion.subject))
    )
    raw = {row[0]: row[1] for row in (await db.execute(stmt)).all()}

    # Normalize: collapse underscores→spaces so "quantitative_aptitude" and
    # "quantitative aptitude" both map to the same bucket.
    def _norm(s: str) -> str:
        return s.lower().replace("_", " ").strip()

    normalized: dict[str, int] = {}
    for k, v in raw.items():
        nk = _norm(k)
        normalized[nk] = normalized.get(nk, 0) + v

    def _count(cat: dict) -> int:
        return (
            normalized.get(_norm(cat["name"]), 0)
            or normalized.get(_norm(cat["key"]), 0)
        )

    return [
        {**cat, "question_count": _count(cat), "has_questions": _count(cat) > 0}
        for cat in QUIZ_CATEGORIES
    ]


async def get_daily_quiz(
    db: AsyncSession, user_id: uuid.UUID, subject: str,
    limit: int = 10, bookmarked_ids: Optional[List[str]] = None,
    difficulty_counts: Optional[dict] = None
) -> list:
    """
    Pattern-diversity quiz with per-question mastery gating + unattempted-first ordering.

    Per-topic draw order within each session:
    1. Unattempted questions (never seen) — always preferred first
    2. Wrong/pending (attempted but never answered correctly) — only after unattempted exhausted
    3. Reserve (soft/fully mastered) — only when both above are empty for all topics

    Mastery rules (based on lifetime correct-answer count per question):
    - correct_count == 0  → primary draw pool (unattempted or wrong-pending)
    - correct_count == 1, NOT bookmarked → reserve only (excluded from primary draw)
    - correct_count == 1, bookmarked → primary draw pool (still learning it)
    - correct_count >= 2  → always excluded, even if bookmarked (fully mastered, retire)

    Topic ordering: discovery-first (never-practised topics come before weak/proficient),
    then by accuracy ascending.  Aims for ≥ min(limit, topic_count) different topics.
    """
    canonical_subject = SUBJECT_KEY_MAP.get(subject.lower(), subject)

    # --- strict per-difficulty selection (user-chosen Easy/Medium/Hard counts) ---
    # When the user picks specific difficulty counts in Quiz Settings, honour them exactly:
    # `limit` becomes the sum, and each draw slot is locked to its difficulty (no fallback
    # to a different level). Otherwise fall back to the auto-balanced 30/30/40 split.
    strict_diff: Optional[dict] = None
    if difficulty_counts:
        norm = {k.upper(): int(v) for k, v in difficulty_counts.items()
                if str(k).upper() in ("EASY", "MEDIUM", "HARD") and int(v) > 0}
        if norm:
            strict_diff = norm
            limit = sum(strict_diff.values())

    # --- per-question correct-answer counts (all-time) ---
    correct_count_rows = (await db.execute(
        select(QuizAttempt.question_id, func.count(QuizAttempt.id).label("cnt"))
        .where(QuizAttempt.user_id == user_id, QuizAttempt.was_correct == True)  # noqa
        .group_by(QuizAttempt.question_id)
    )).all()
    correct_counts: dict = {row[0]: row[1] for row in correct_count_rows}

    # --- all-time attempted question IDs (for unattempted-first ordering) ---
    all_attempted_ids: set = set(r[0] for r in (await db.execute(
        select(QuizAttempt.question_id).where(QuizAttempt.user_id == user_id).distinct()
    )).all())

    # correct once  → soft-mastered (excluded unless bookmarked)
    mastered_once: set = {qid for qid, cnt in correct_counts.items() if cnt == 1}
    # correct ≥ 2   → fully mastered (excluded even if bookmarked)
    mastered_fully: set = {qid for qid, cnt in correct_counts.items() if cnt >= 2}

    # Parse bookmarked IDs — these exempt questions from mastered_once exclusion
    exempt: set = set()
    if bookmarked_ids:
        for bid in bookmarked_ids:
            try:
                exempt.add(uuid.UUID(str(bid)))
            except (ValueError, AttributeError):
                pass

    # Primary draw exclusion: soft-mastered (not bookmarked) + fully mastered
    excluded_from_primary: set = (mastered_once - exempt) | mastered_fully
    # Reserve pool (shown only when primary is exhausted)
    reserve_ids: set = excluded_from_primary

    # Get all distinct topic_codes for this subject
    tc_rows = (await db.execute(
        select(QuizQuestion.topic_code, QuizQuestion.topic)
        .where(_subj_match(canonical_subject))
        .distinct()
    )).all()

    pattern_map: dict[str, str] = {}
    for tc, topic in tc_rows:
        key = tc if tc else f"_topic_{topic or 'general'}"
        if key not in pattern_map:
            pattern_map[key] = topic or "General"

    if not pattern_map:
        raw = (await db.execute(
            select(QuizQuestion)
            .where(_subj_match(canonical_subject))
            .order_by(func.random()).limit(limit)
        )).scalars().all()
        expanded = await _expand_passage_groups(db, list(raw))
        return [_serialize_quiz_question(q) for q in expanded]

    # Load topic mastery records for topic-priority ordering
    code_keys = [k for k in pattern_map if not k.startswith("_topic_")]
    mastery_map: dict[str, "UserTopicMastery"] = {}
    if code_keys:
        rows = (await db.execute(
            select(UserTopicMastery).where(
                UserTopicMastery.user_id == user_id,
                UserTopicMastery.topic_code.in_(code_keys)
            )
        )).scalars().all()
        mastery_map = {m.topic_code: m for m in rows}

    # Topic priority:
    # 0 = never attempted (discovery) → highest
    # 1 = weak         accuracy < 50%
    # 2 = improving    accuracy 50-70%
    # 3 = proficient   accuracy ≥ 70%
    def _priority(key: str) -> int:
        m = mastery_map.get(key)
        if not m or m.attempted_count == 0:
            return 0
        if m.current_accuracy < 50:
            return 1
        if m.current_accuracy < 70:
            return 2
        return 3

    sorted_patterns = sorted(pattern_map.keys(), key=lambda k: (_priority(k), random.random()))

    # Aim for ≥ min(limit, topic_count) different topics. When there are at least `limit`
    # topics we take one question from each (maximum spread — more questions => more topics).
    # When the subject has fewer topics than `limit`, we take a few from each (ceil division)
    # so the quiz still fills from real topics rather than random backfill.
    patterns_to_use = sorted_patterns[:limit]
    per_pattern = max(1, -(-limit // len(patterns_to_use)))  # ceil division

    # Difficulty plan across the whole quiz. In strict mode the plan is exactly the
    # user-chosen per-difficulty counts; otherwise it's the auto-balanced 3 easy / 3 medium /
    # 4 hard per 10 (30/30/40), scaled to `limit`. Each primary draw slot targets one
    # difficulty; in the balanced (non-strict) mode it falls back to any difficulty if the
    # topic has none of the target level, so the quiz always fills.
    if strict_diff:
        diff_plan = []
        for d in ("EASY", "MEDIUM", "HARD"):
            diff_plan += [d] * strict_diff.get(d, 0)
    else:
        n_easy = round(limit * 0.30)
        n_hard = round(limit * 0.40)
        n_med = max(0, limit - n_easy - n_hard)
        diff_plan = ["EASY"] * n_easy + ["MEDIUM"] * n_med + ["HARD"] * n_hard
    random.shuffle(diff_plan)
    diff_iter = iter(diff_plan)

    seen_ids: set = set()
    result_questions: list = []
    reserve_questions: list = []  # collected for fallback

    for key in patterns_to_use:
        if len(result_questions) >= limit:
            break
        quota = min(per_pattern, limit - len(result_questions))

        if key.startswith("_topic_"):
            topic_text = pattern_map[key]
            base_cond = [
                _subj_match(canonical_subject),
                func.lower(QuizQuestion.topic) == topic_text.lower(),
                QuizQuestion.topic_code.is_(None),
            ]
        else:
            base_cond = [
                _subj_match(canonical_subject),
                QuizQuestion.topic_code == key,
            ]

        # Primary draw — Phase A: unattempted questions (never seen, always preferred),
        # each slot targeting the next difficulty from the balanced plan.
        exclude_primary = excluded_from_primary | seen_ids
        primary_qs: list = []
        for _slot in range(quota):
            target_diff = next(diff_iter, None)
            picked = None
            # Try the target difficulty first. In strict mode stop there (never substitute a
            # different level); in balanced mode fall back to any difficulty so it always fills.
            diff_fallbacks = [target_diff] if target_diff else []
            if not strict_diff:
                diff_fallbacks = diff_fallbacks + [None]
            for diff_filter in diff_fallbacks:
                unatt_exclude = exclude_primary | all_attempted_ids | {q.id for q in primary_qs}
                cond = list(base_cond)
                if unatt_exclude:
                    cond.append(QuizQuestion.id.not_in(unatt_exclude))
                if diff_filter:
                    cond.append(
                        func.upper(func.coalesce(QuizQuestion.difficulty, "MEDIUM")) == diff_filter
                    )
                picked = (await db.execute(
                    select(QuizQuestion).where(*cond).order_by(func.random()).limit(1)
                )).scalars().first()
                if picked:
                    break
            if picked:
                primary_qs.append(picked)

        # Phase B: wrong/pending — attempted but never answered correctly, only fills gap.
        # Skipped in strict mode (these are difficulty-blind; strict fills by exact level below).
        if len(primary_qs) < quota and not strict_diff:
            wrong_pending = all_attempted_ids - excluded_from_primary - seen_ids - {q.id for q in primary_qs}
            if wrong_pending:
                wp_cond = list(base_cond) + [QuizQuestion.id.in_(wrong_pending)]
                wp_qs = (await db.execute(
                    select(QuizQuestion).where(*wp_cond)
                    .order_by(func.random()).limit(quota - len(primary_qs))
                )).scalars().all()
                primary_qs.extend(wp_qs)

        # Collect reserve for this topic (used only when primary is exhausted; balanced mode only)
        if len(primary_qs) < quota and reserve_ids and not strict_diff:
            res_pool = reserve_ids - seen_ids - {q.id for q in primary_qs}
            if res_pool:
                rq = (await db.execute(
                    select(QuizQuestion).where(*base_cond, QuizQuestion.id.in_(res_pool))
                    .order_by(func.random()).limit(quota - len(primary_qs))
                )).scalars().all()
                reserve_questions.extend(rq)

        for q in primary_qs:
            seen_ids.add(q.id)
            result_questions.append(q)

    if strict_diff:
        # Strict mode: top up each difficulty to its exact requested count, pulling only that
        # level from the subject (unattempted-first, then any). Guarantees the chosen mix.
        def _qdiff(q) -> str:
            return (q.difficulty or "MEDIUM").upper()
        for diff, want in strict_diff.items():
            have = sum(1 for q in result_questions if _qdiff(q) == diff)
            need = want - have
            if need <= 0:
                continue
            already = {q.id for q in result_questions}
            for extra_exclude in (already | all_attempted_ids, already):
                if need <= 0:
                    break
                cond = [
                    _subj_match(canonical_subject),
                    func.upper(func.coalesce(QuizQuestion.difficulty, "MEDIUM")) == diff,
                ]
                if extra_exclude:
                    cond.append(QuizQuestion.id.not_in(extra_exclude))
                fillers = (await db.execute(
                    select(QuizQuestion).where(*cond).order_by(func.random()).limit(need)
                )).scalars().all()
                for q in fillers:
                    if q.id not in already:
                        result_questions.append(q)
                        already.add(q.id)
                        need -= 1
                        if need <= 0:
                            break
    else:
        # Fill remaining slots from reserve (primary pool exhausted across all topics)
        if len(result_questions) < limit and reserve_questions:
            already = {q.id for q in result_questions}
            for q in reserve_questions:
                if q.id not in already and len(result_questions) < limit:
                    result_questions.append(q)
                    already.add(q.id)

        # Last resort: fill from the subject. Prefer never-attempted questions to avoid
        # showing repeats; only reuse already-attempted questions if nothing else is left.
        if len(result_questions) < limit:
            already = {q.id for q in result_questions}
            for extra_exclude in (already | all_attempted_ids, already):
                if len(result_questions) >= limit:
                    break
                any_cond = [_subj_match(canonical_subject)]
                if extra_exclude:
                    any_cond.append(QuizQuestion.id.not_in(extra_exclude))
                fillers = (await db.execute(
                    select(QuizQuestion).where(*any_cond)
                    .order_by(func.random()).limit(limit - len(result_questions))
                )).scalars().all()
                for q in fillers:
                    if q.id not in already:
                        result_questions.append(q)
                        already.add(q.id)
                        if len(result_questions) >= limit:
                            break

    random.shuffle(result_questions)
    expanded = await _expand_passage_groups(db, result_questions[:limit])
    return [_serialize_quiz_question(q) for q in expanded]


async def get_weak_topic_quiz(db: AsyncSession, user_id: uuid.UUID, limit: int = 10) -> dict:
    """
    Personalized practice quiz.
    - If user has weak topics (from mocks / PYQs / quiz practice): suggested questions first,
      then high-priority fill to always give `limit` questions.
    - If no weak topics yet: return high-priority unattempted questions across a balanced subject mix,
      so the student can practice from day 1 without needing a mock test first.
    """
    stmt = (
        select(UserWeakTopic)
        .where(UserWeakTopic.user_id == user_id, UserWeakTopic.accuracy < 60.0)
        .order_by(UserWeakTopic.accuracy.asc()).limit(5)
    )
    weak_topics = (await db.execute(stmt)).scalars().all()

    # Get user's attempted + wrong question IDs (needed for both paths)
    attempted_ids = set(r[0] for r in (await db.execute(
        select(QuizAttempt.question_id).where(QuizAttempt.user_id == user_id)
    )).all())
    wrong_ids = set(r[0] for r in (await db.execute(
        select(QuizAttempt.question_id).where(
            QuizAttempt.user_id == user_id, QuizAttempt.was_correct == False  # noqa
        )
    )).all())

    questions = []
    weak_topic_info = []

    # ── Path 1: we have weak topics → suggested-first ──
    for wt in weak_topics:
        display_info = None
        if wt.topic_code:
            display_info = await taxonomy_service.resolve_topic_code(db, wt.topic_code)

        display_subject = display_info["subject"] if display_info else wt.subject
        display_topic = display_info["topic"] if display_info else (wt.topic or "General")

        mastery = await _get_or_create_mastery(db, user_id, display_subject, display_topic, wt.topic_code)

        weak_topic_info.append({
            "subject": display_subject,
            "topic": display_topic,
            "topic_code": wt.topic_code,
            "accuracy": round(wt.accuracy, 1),
            "total_attempted": wt.total_questions,
            "mastery_level": mastery.mastery_level if mastery else "NEEDS_WORK",
            "coverage": f"{mastery.attempted_count}/{mastery.total_available}" if mastery else "0/0",
        })

        per_topic = max(2, limit // max(1, len(weak_topics)))
        topic_qs = await _fetch_prioritized_questions(
            db, wt.topic_code, display_subject, display_topic, per_topic, attempted_ids, wrong_ids
        )
        questions.extend(topic_qs)

    # Deduplicate suggested pool
    seen = set()
    unique_qs = []
    for q in questions:
        if q.id not in seen:
            seen.add(q.id)
            unique_qs.append(q)

    suggested_count = len(unique_qs)

    # ── Path 2: fill remainder with high-priority practice so we ALWAYS return `limit` questions ──
    if len(unique_qs) < limit:
        already = set(q.id for q in unique_qs)
        exclude = already | attempted_ids  # prefer unattempted first
        fill_stmt = (
            select(QuizQuestion)
            .where(QuizQuestion.id.not_in(exclude) if exclude else True)
            .order_by(func.random())
            .limit(limit - len(unique_qs))
        )
        fillers = (await db.execute(fill_stmt)).scalars().all()

        # If still short (user has attempted huge chunk), open to wrong-answer revisits
        if len(fillers) < limit - len(unique_qs) and wrong_ids:
            extra_exclude = already | {f.id for f in fillers}
            pool = wrong_ids - extra_exclude
            if pool:
                more = (await db.execute(
                    select(QuizQuestion).where(QuizQuestion.id.in_(pool))
                    .order_by(func.random()).limit(limit - len(unique_qs) - len(fillers))
                )).scalars().all()
                fillers.extend(more)

        # Last resort: any question, even attempted
        if len(fillers) < limit - len(unique_qs):
            extra_exclude = already | {f.id for f in fillers}
            any_stmt = (
                select(QuizQuestion)
                .where(QuizQuestion.id.not_in(extra_exclude) if extra_exclude else True)
                .order_by(func.random()).limit(limit - len(unique_qs) - len(fillers))
            )
            fillers.extend((await db.execute(any_stmt)).scalars().all())

        unique_qs.extend(fillers)

    # Build messaging
    if weak_topic_info:
        message = (f"Based on your performance, we found {len(weak_topic_info)} weak area(s) to improve. "
                   f"Showing {suggested_count} suggested question(s) + extra practice.")
    else:
        message = "Practice mode — keep answering to help us learn your strengths and weaknesses."

    final_qs = await _expand_passage_groups(db, unique_qs[:limit])
    return {
        "questions": [_serialize_quiz_question(q) for q in final_qs],
        "weak_topics": weak_topic_info,
        "suggested_count": suggested_count,
        "total_available": await _count_weak_topic_questions(db, weak_topics) if weak_topics else 0,
        "message": message,
    }


async def _fetch_prioritized_questions(
    db: AsyncSession, topic_code: Optional[str], subject: str, topic: str,
    limit: int, attempted_ids: set, wrong_ids: set
) -> list:
    """
    Fetch quiz questions with smart prioritization:
    Phase 1: By topic_code (exact) — unattempted, EASY→MED→HARD
    Phase 2: By topic_code (exact) — previously wrong
    Phase 3: By subject+topic text match — fallback
    Phase 4: By subject only — last resort
    """
    difficulty_order = case(
        (QuizQuestion.difficulty == "EASY", 1),
        (QuizQuestion.difficulty == "MEDIUM", 2),
        (QuizQuestion.difficulty == "HARD", 3),
        else_=2
    )

    result_qs = []

    # Phase 1: Exact topic_code match — unattempted first
    if topic_code:
        conditions = [QuizQuestion.topic_code == topic_code]
        if attempted_ids:
            conditions.append(QuizQuestion.id.not_in(attempted_ids))

        unattempted = (await db.execute(
            select(QuizQuestion).where(*conditions)
            .order_by(difficulty_order, func.random()).limit(limit)
        )).scalars().all()
        result_qs.extend(unattempted)

    # Phase 2: Exact topic_code match — previously wrong
    if topic_code and len(result_qs) < limit and wrong_ids:
        existing = {q.id for q in result_qs}
        pool = wrong_ids - existing
        if pool:
            wrong_qs = (await db.execute(
                select(QuizQuestion).where(
                    QuizQuestion.topic_code == topic_code, QuizQuestion.id.in_(pool)
                ).order_by(difficulty_order, func.random()).limit(limit - len(result_qs))
            )).scalars().all()
            result_qs.extend(wrong_qs)

    # Phase 3: Subject + topic text fallback (for questions without topic_code)
    if len(result_qs) < limit:
        existing = {q.id for q in result_qs}
        text_conditions = [_subj_match(subject)]
        if topic:
            text_conditions.append(func.lower(QuizQuestion.topic) == topic.lower())
        if existing:
            text_conditions.append(QuizQuestion.id.not_in(existing))

        fallback = (await db.execute(
            select(QuizQuestion).where(*text_conditions)
            .order_by(func.random()).limit(limit - len(result_qs))
        )).scalars().all()
        result_qs.extend(fallback)

    # Phase 4: Subject-only last resort
    if len(result_qs) < limit:
        existing = {q.id for q in result_qs}
        subj_cond = [_subj_match(subject)]
        if existing:
            subj_cond.append(QuizQuestion.id.not_in(existing))
        fallback2 = (await db.execute(
            select(QuizQuestion).where(*subj_cond)
            .order_by(func.random()).limit(limit - len(result_qs))
        )).scalars().all()
        result_qs.extend(fallback2)

    return result_qs[:limit]


async def get_wrong_practice_quiz(
    db: AsyncSession, user_id: uuid.UUID,
    bookmarked_ids: Optional[List[str]] = None, limit: int = 20
) -> dict:
    """
    "Revise Weak Areas" mode — returns questions from three pools:
    1. Wrong/skipped: ever attempted incorrectly AND never since answered correctly
    2. Bookmarked: passed from client AsyncStorage (user flagged them for review)
    Pools are merged, deduplicated, then returned in random order.
    """
    # Per-question correct-answer counts (all-time)
    correct_count_rows = (await db.execute(
        select(QuizAttempt.question_id, func.count(QuizAttempt.id).label("cnt"))
        .where(QuizAttempt.user_id == user_id, QuizAttempt.was_correct == True)  # noqa
        .group_by(QuizAttempt.question_id)
    )).all()
    mastered: set = {row[0] for row in correct_count_rows if row[1] >= 1}

    wrong_raw: set = set(r[0] for r in (await db.execute(
        select(QuizAttempt.question_id).where(
            QuizAttempt.user_id == user_id, QuizAttempt.was_correct == False  # noqa
        ).distinct()
    )).all())
    wrong_ids = wrong_raw - mastered  # pending a first correct answer

    bookmarked: set = set()
    if bookmarked_ids:
        for bid in bookmarked_ids:
            try:
                bookmarked.add(uuid.UUID(str(bid)))
            except (ValueError, AttributeError):
                pass

    combined: set = wrong_ids | bookmarked

    if not combined:
        return {
            "questions": [], "count": 0, "total_available": 0,
            "wrong_count": 0, "bookmarked_count": len(bookmarked),
            "message": "No weak questions found — great work! Keep practising to stay sharp.",
        }

    questions = (await db.execute(
        select(QuizQuestion).where(QuizQuestion.id.in_(combined))
        .order_by(func.random()).limit(limit)
    )).scalars().all()

    return {
        "questions": [_serialize_quiz_question(q) for q in questions],
        "count": len(questions),
        "total_available": len(combined),
        "wrong_count": len(wrong_ids),
        "bookmarked_count": len(bookmarked),
        "message": (
            f"{len(combined)} questions to revise"
            + (f" · {len(wrong_ids)} wrong/skipped" if wrong_ids else "")
            + (f" · {len(bookmarked)} bookmarked" if bookmarked else "")
        ),
    }


async def get_more_practice(db: AsyncSession, user_id: uuid.UUID, subject: str,
                            topic: Optional[str] = None, topic_code: Optional[str] = None,
                            exclude_ids: List[str] = [], limit: int = 10) -> dict:
    """Get more practice questions from the same topic."""
    exclude_uuids = [uuid.UUID(eid) for eid in exclude_ids if eid]

    # Primary: match by topic_code
    if topic_code:
        conditions = [QuizQuestion.topic_code == topic_code]
    else:
        conditions = [_subj_match(subject)]
        if topic:
            conditions.append(func.lower(QuizQuestion.topic) == topic.lower())

    if exclude_uuids:
        conditions.append(QuizQuestion.id.not_in(exclude_uuids))

    questions = (await db.execute(
        select(QuizQuestion).where(*conditions).order_by(func.random()).limit(limit)
    )).scalars().all()

    # Count remaining
    all_exclude = exclude_uuids + [q.id for q in questions]
    count_cond = [QuizQuestion.topic_code == topic_code] if topic_code else [_subj_match(subject)]
    if all_exclude:
        count_cond.append(QuizQuestion.id.not_in(all_exclude))
    remaining = (await db.execute(select(func.count(QuizQuestion.id)).where(*count_cond))).scalar() or 0

    return {
        "questions": [_serialize_quiz_question(q) for q in questions],
        "remaining_count": remaining,
        "has_more": remaining > 0,
        "message": f"{remaining} more questions available" if remaining > 0 else "You've exhausted all questions in this topic! 🎉"
    }


async def submit_quiz_answers(db: AsyncSession, user_id: uuid.UUID, answers: List[dict]) -> dict:
    from app.models.user import User
    from fastapi import HTTPException

    correct = 0
    skipped = 0
    total = len(answers)
    details = []
    topic_stats = {}  # topic_code → {correct, total, subject, topic}

    # Parse + validate question IDs once, then fetch every QuizQuestion in a
    # single round-trip. The previous code issued one SELECT per answer, which
    # turned a 30-question quiz submit into 30 sequential DB hops over a high-
    # latency Railway link. With many concurrent submitters this also held a
    # DB connection from the (small) pool for the entire duration of the loop.
    parsed_ids: List[uuid.UUID] = []
    for ans in answers:
        raw_qid = ans.get("question_id")
        if not raw_qid:
            raise HTTPException(status_code=400, detail="Every answer must include a question_id.")
        try:
            parsed_ids.append(uuid.UUID(str(raw_qid)))
        except (ValueError, TypeError):
            raise HTTPException(status_code=400, detail=f"Invalid question_id: {raw_qid!r}.")

    questions_by_id = {}
    if parsed_ids:
        rows = (await db.execute(
            select(QuizQuestion).where(QuizQuestion.id.in_(parsed_ids))
        )).scalars().all()
        questions_by_id = {q.id: q for q in rows}

    for ans, q_id in zip(answers, parsed_ids):
        selected_index = ans.get("selected_option_index")
        question = questions_by_id.get(q_id)

        was_correct = False
        correct_index = None

        if question and question.options:
            for i, opt in enumerate(question.options):
                if opt.get("is_correct", False):
                    correct_index = i
                    break
            if selected_index is not None:
                try:
                    was_correct = question.options[selected_index].get("is_correct", False)
                except (IndexError, TypeError):
                    was_correct = False

        if was_correct:
            correct += 1
        if selected_index is None:
            skipped += 1

        db.add(QuizAttempt(user_id=user_id, question_id=q_id, was_correct=was_correct))

        if question:
            details.append({
                "question_id": str(q_id), "question_text": question.question_text,
                "was_correct": was_correct, "selected_option_index": selected_index,
                "correct_option_index": correct_index, "explanation": question.explanation or ""
            })

            # Track by topic_code (deterministic), normalised via taxonomy
            canon_subj, canon_topic, canon_code = await taxonomy_service.normalize(
                db, question.subject or "General Knowledge", question.topic or "General", question.topic_code
            )
            tc = canon_code or f"__{canon_subj}_{canon_topic}"
            if tc not in topic_stats:
                topic_stats[tc] = {"correct": 0, "total": 0, "subject": canon_subj,
                                   "topic": canon_topic, "topic_code": canon_code}
            topic_stats[tc]["total"] += 1
            if was_correct:
                topic_stats[tc]["correct"] += 1

    await _update_streak(db, user_id)

    # Update mastery per topic
    for tc, stats in topic_stats.items():
        await _update_mastery(db, user_id, stats["subject"], stats["topic"],
                              stats["topic_code"], stats["correct"], stats["total"])

    # Feed weak-topic signal from quiz practice (not only mocks)
    for tc, stats in topic_stats.items():
        await _upsert_weak_topic(
            db, user_id,
            subject=stats["subject"], topic=stats["topic"], topic_code=stats["topic_code"],
            correct=stats["correct"], total=stats["total"],
        )

    user = (await db.execute(select(User).where(User.id == user_id))).scalars().first()

    # Gamification
    points_earned = correct * 10
    old_stars = user.stars if user else 0
    new_star_unlocked = False
    new_stars = old_stars

    if user:
        user.points = (user.points or 0) + points_earned
        total_points = user.points
        if total_points >= 50000: new_stars = 5
        elif total_points >= 15000: new_stars = 4
        elif total_points >= 5000: new_stars = 3
        elif total_points >= 2000: new_stars = 2
        elif total_points >= 500: new_stars = 1
        if new_stars > old_stars:
            user.stars = new_stars
            new_star_unlocked = True
        db.add(user)

    # Single commit covering: quiz attempts + streak + mastery + weak-topic + user points/stars
    await db.commit()

    accuracy = (correct / total * 100) if total > 0 else 0
    answered = total - skipped
    score_percentage = (correct / answered * 100) if answered > 0 else 0

    mastery_info = []
    for tc, stats in topic_stats.items():
        mastery = await _get_or_create_mastery(db, user_id, stats["subject"], stats["topic"], stats["topic_code"])
        if mastery:
            mastery_info.append({
                "subject": stats["subject"], "topic": stats["topic"],
                "topic_code": stats["topic_code"],
                "mastery_level": mastery.mastery_level,
                "accuracy": round(mastery.current_accuracy, 1),
                "coverage": f"{mastery.attempted_count}/{mastery.total_available}",
            })

    # Identify THIS session's weak spots (for the scorecard focus-areas panel)
    session_weak_topics = [
        {"subject": s["subject"], "topic": s["topic"], "topic_code": s["topic_code"],
         "accuracy": round((s["correct"] / s["total"] * 100) if s["total"] else 0, 1)}
        for s in topic_stats.values() if s["total"] >= 2 and (s["correct"] / s["total"]) < 0.6
    ]

    nudge = _get_encouragement(accuracy)

    return {
        "total": total,
        "correct": correct,
        "incorrect": answered - correct,
        "skipped": skipped,
        "accuracy": round(accuracy, 1),
        "score_percentage": round(score_percentage, 1),
        "details": details,
        "encouragement": nudge,
        "nudge": nudge,
        "mastery": mastery_info,
        "weak_topics": session_weak_topics,
        "points_earned": points_earned,
        "total_points": user.points if user else 0,
        "stars": user.stars if user else 0,
        "new_star_unlocked": new_star_unlocked,
    }


async def update_weak_topics_from_attempt(db: AsyncSession, user_id: uuid.UUID, attempt_id: uuid.UUID):
    """
    Called after mock test submission. Extracts topic_code from each question
    and upserts UserWeakTopic with deterministic codes.
    """
    stmt = (
        select(UserAnswer).options(selectinload(UserAnswer.question))
        .where(UserAnswer.attempt_id == attempt_id)
    )
    answers = (await db.execute(stmt)).scalars().all()

    topic_map = {}  # topic_code → {correct, total, subject, topic}

    for ans in answers:
        if not ans.question:
            continue

        raw_subj = ans.question.subject or "General Knowledge"
        raw_topic = ans.question.topic or "General"
        raw_code = ans.question.topic_code

        # Resolve via taxonomy: deterministic if topic_code exists, fuzzy fallback otherwise
        canon_subj, canon_topic, canon_code = await taxonomy_service.normalize(
            db, raw_subj, raw_topic, raw_code
        )

        key = canon_code or f"__{canon_subj}_{canon_topic}"

        if key not in topic_map:
            topic_map[key] = {"correct": 0, "total": 0, "subject": canon_subj,
                              "topic": canon_topic, "topic_code": canon_code}

        topic_map[key]["total"] += 1

        if ans.selected_option_index is not None:
            try:
                selected_opt = ans.question.options[ans.selected_option_index]
                if selected_opt.get("is_correct", False):
                    topic_map[key]["correct"] += 1
            except (IndexError, TypeError):
                pass

    # Upsert UserWeakTopic — match by topic_code (deterministic)
    for key, stats in topic_map.items():
        await _upsert_weak_topic(
            db, user_id,
            subject=stats["subject"], topic=stats["topic"], topic_code=stats["topic_code"],
            correct=stats["correct"], total=stats["total"],
        )

    await db.commit()


async def _upsert_weak_topic(
    db: AsyncSession, user_id: uuid.UUID,
    *, subject: str, topic: str, topic_code: Optional[str],
    correct: int, total: int,
) -> None:
    """
    Shared upsert for UserWeakTopic. Called from BOTH
    (a) mock-test submission (via `update_weak_topics_from_attempt`), and
    (b) practice-quiz submission (via `submit_quiz_answers`).
    Caller is responsible for commit.
    """
    if total <= 0:
        return

    existing = None
    if topic_code:
        existing = (await db.execute(
            select(UserWeakTopic).where(
                UserWeakTopic.user_id == user_id, UserWeakTopic.topic_code == topic_code
            )
        )).scalars().first()

    if not existing:
        existing = (await db.execute(
            select(UserWeakTopic).where(
                UserWeakTopic.user_id == user_id,
                UserWeakTopic.subject == subject,
                UserWeakTopic.topic == topic,
            )
        )).scalars().first()

    if existing:
        existing.total_questions += total
        existing.correct_count += correct
        existing.accuracy = (
            (existing.correct_count / existing.total_questions * 100)
            if existing.total_questions > 0 else 0
        )
        if topic_code and not existing.topic_code:
            existing.topic_code = topic_code  # backfill code for legacy records
        db.add(existing)
    else:
        accuracy = (correct / total * 100) if total > 0 else 0
        db.add(UserWeakTopic(
            user_id=user_id, subject=subject, topic=topic,
            topic_code=topic_code, accuracy=accuracy,
            total_questions=total, correct_count=correct,
        ))


async def upload_quiz_questions(db: AsyncSession, questions: List[dict]) -> dict:
    """Bulk insert with taxonomy normalization. topic_code is the key field."""
    created = 0
    normalized_count = 0
    missing_codes = []

    for q in questions:
        raw_subject = q.get("subject", "General Knowledge")
        raw_topic = q.get("topic", "General")
        raw_code = q.get("topic_code")

        # Resolve via taxonomy
        canon_subj, canon_topic, canon_code = await taxonomy_service.normalize(
            db, raw_subject, raw_topic, raw_code
        )

        was_normalized = (canon_subj != raw_subject or canon_topic != raw_topic or
                          (raw_code and canon_code and canon_code != raw_code))
        if was_normalized:
            normalized_count += 1

        # Track questions without valid topic_code
        if not canon_code:
            missing_codes.append(f"{raw_subject} / {raw_topic}")

        quiz_q = QuizQuestion(
            question_text=q.get("question_text", ""),
            image_url=q.get("image_url"),
            diagram_svg=q.get("diagram_svg"),
            explanation=q.get("explanation", ""),
            explanation_svg=q.get("explanation_svg"),
            difficulty=q.get("difficulty", "MEDIUM"),
            subject=canon_subj,
            topic=canon_topic,
            topic_code=canon_code or raw_code,  # Use provided code even if not in taxonomy
            options=[{
                "option_text": opt.get("option_text", ""),
                "is_correct": opt.get("is_correct", False)
            } for opt in q.get("options", [])]
        )
        db.add(quiz_q)
        created += 1

    await db.commit()

    # Deduplicate missing codes
    missing_unique = list(set(missing_codes))

    return {
        "created": created,
        "normalized": normalized_count,
        "missing_topic_codes": missing_unique[:20],  # Cap at 20
        "message": f"Successfully added {created} questions. {normalized_count} tags auto-normalized."
            + (f" {len(missing_unique)} question(s) have no matching topic_code." if missing_unique else "")
    }


async def get_streak_info(db: AsyncSession, user_id: uuid.UUID) -> dict:
    stmt = select(UserStreak).where(UserStreak.user_id == user_id)
    streak = (await db.execute(stmt)).scalars().first()

    if not streak:
        return {"current_streak": 0, "longest_streak": 0, "is_active_today": False,
                "freeze_available": True, "nudge": "Start your streak today! 🔥"}

    today = datetime.utcnow().date()
    is_active = streak.last_active_date and streak.last_active_date.date() == today
    at_risk = streak.last_active_date and streak.last_active_date.date() == today - timedelta(days=1) and not is_active

    if streak.current_streak >= 30:
        nudge = f"🏆 Legendary! {streak.current_streak}-day streak!"
    elif streak.current_streak >= 7:
        nudge = f"🔥 {streak.current_streak}-day streak! Keep going!"
    elif at_risk:
        nudge = f"⚠️ Your {streak.current_streak}-day streak is at risk! Practice now!"
    elif is_active:
        nudge = f"✅ {streak.current_streak}-day streak active!"
    else:
        nudge = "Start your streak today! 🔥"

    return {"current_streak": streak.current_streak, "longest_streak": streak.longest_streak,
            "is_active_today": is_active, "freeze_available": streak.freeze_available,
            "at_risk": at_risk if streak.current_streak > 0 else False, "nudge": nudge}


# ─── Private helpers ───

async def _update_streak(db: AsyncSession, user_id: uuid.UUID):
    streak = (await db.execute(select(UserStreak).where(UserStreak.user_id == user_id))).scalars().first()
    today = datetime.utcnow().date()

    if not streak:
        db.add(UserStreak(user_id=user_id, current_streak=1, longest_streak=1, last_active_date=datetime.utcnow()))
        return

    if streak.last_active_date:
        last_date = streak.last_active_date.date()
        if last_date == today:
            return
        elif last_date == today - timedelta(days=1):
            streak.current_streak += 1
        else:
            streak.current_streak = 1
    else:
        streak.current_streak = 1

    streak.longest_streak = max(streak.longest_streak, streak.current_streak)
    streak.last_active_date = datetime.utcnow()
    db.add(streak)


async def _get_or_create_mastery(db: AsyncSession, user_id: uuid.UUID,
                                  subject: str, topic: str, topic_code: Optional[str] = None) -> Optional[UserTopicMastery]:
    # Primary: find by topic_code
    mastery = None
    if topic_code:
        mastery = (await db.execute(
            select(UserTopicMastery).where(
                UserTopicMastery.user_id == user_id, UserTopicMastery.topic_code == topic_code
            )
        )).scalars().first()

    # Fallback: by text
    if not mastery:
        mastery = (await db.execute(
            select(UserTopicMastery).where(
                UserTopicMastery.user_id == user_id,
                UserTopicMastery.subject == subject, UserTopicMastery.topic == topic
            )
        )).scalars().first()

    if not mastery:
        # Count available questions
        if topic_code:
            count_stmt = select(func.count(QuizQuestion.id)).where(QuizQuestion.topic_code == topic_code)
        else:
            count_stmt = select(func.count(QuizQuestion.id)).where(
                _subj_match(subject),
                func.lower(QuizQuestion.topic) == topic.lower()
            )
        total_avail = (await db.execute(count_stmt)).scalar() or 0

        mastery = UserTopicMastery(
            user_id=user_id, subject=subject, topic=topic,
            topic_code=topic_code, total_available=total_avail,
        )
        db.add(mastery)
        await db.flush()

    return mastery


async def _update_mastery(db: AsyncSession, user_id: uuid.UUID, subject: str, topic: str,
                          topic_code: Optional[str], correct: int, total: int):
    mastery = await _get_or_create_mastery(db, user_id, subject, topic, topic_code)
    if not mastery:
        return

    mastery.attempted_count += total
    mastery.correct_count += correct
    mastery.current_accuracy = (mastery.correct_count / mastery.attempted_count * 100) if mastery.attempted_count > 0 else 0
    mastery.last_practiced_at = datetime.utcnow()

    # Refresh total_available
    if topic_code:
        mastery.total_available = (await db.execute(
            select(func.count(QuizQuestion.id)).where(QuizQuestion.topic_code == topic_code)
        )).scalar() or 0
    else:
        mastery.total_available = (await db.execute(
            select(func.count(QuizQuestion.id)).where(
                _subj_match(subject),
                func.lower(QuizQuestion.topic) == topic.lower()
            )
        )).scalar() or 0

    # Mastery level
    coverage = (mastery.attempted_count / mastery.total_available * 100) if mastery.total_available > 0 else 0
    acc = mastery.current_accuracy
    if acc >= 80 and coverage >= 75:
        mastery.mastery_level = "MASTERED"
    elif acc >= 60:
        mastery.mastery_level = "PROFICIENT"
    elif acc >= 40:
        mastery.mastery_level = "IMPROVING"
    else:
        mastery.mastery_level = "NEEDS_WORK"

    db.add(mastery)


async def _expand_passage_groups(db: AsyncSession, questions: list) -> list:
    """For any question that belongs to a passage group (passage_id set),
    fetch all sibling questions from that passage and insert them as a
    contiguous block right after the first occurrence of that passage_id.
    Deduplicates so siblings already in the list aren't repeated."""
    passage_ids = [q.passage_id for q in questions if q.passage_id]
    if not passage_ids:
        return questions

    unique_pids = list(dict.fromkeys(passage_ids))  # preserve order, dedupe

    # Fetch all siblings in one round-trip
    siblings_by_pid: dict[str, list] = {}
    for pid in unique_pids:
        rows = (await db.execute(
            select(QuizQuestion).where(QuizQuestion.passage_id == pid)
        )).scalars().all()
        siblings_by_pid[pid] = rows

    seen_ids: set = set()
    result: list = []
    inserted_pids: set = set()

    for q in questions:
        if q.id in seen_ids:
            continue
        seen_ids.add(q.id)
        result.append(q)

        if q.passage_id and q.passage_id not in inserted_pids:
            inserted_pids.add(q.passage_id)
            for sibling in siblings_by_pid.get(q.passage_id, []):
                if sibling.id not in seen_ids:
                    seen_ids.add(sibling.id)
                    result.append(sibling)

    return result


async def _count_weak_topic_questions(db, weak_topics) -> int:
    total = 0
    for wt in weak_topics:
        if wt.topic_code:
            count = (await db.execute(
                select(func.count(QuizQuestion.id)).where(QuizQuestion.topic_code == wt.topic_code)
            )).scalar() or 0
        else:
            conds = [_subj_match(wt.subject)]
            if wt.topic:
                conds.append(func.lower(QuizQuestion.topic) == wt.topic.lower())
            count = (await db.execute(select(func.count(QuizQuestion.id)).where(*conds))).scalar() or 0
        total += count
    return total


def _serialize_quiz_question(q: QuizQuestion) -> dict:
    return {
        "id": str(q.id), "question_text": q.question_text, "image_url": q.image_url,
        "diagram_svg": q.diagram_svg, "explanation_svg": q.explanation_svg,
        "subject": q.subject, "topic": q.topic, "topic_code": q.topic_code,
        "passage_id": q.passage_id,
        "difficulty": q.difficulty, "explanation": q.explanation,
        "options": [{"option_text": o.get("option_text"), "is_correct": o.get("is_correct")} for o in q.options]
    }


def _get_encouragement(accuracy: float) -> str:
    if accuracy >= 90:
        return "🏆 Outstanding! You're absolutely crushing it!"
    elif accuracy >= 80:
        return "🌟 Excellent work! Keep this momentum!"
    elif accuracy >= 60:
        return "💪 Good effort! A bit more practice and you'll master this!"
    elif accuracy >= 40:
        return "📚 Keep going! Every question makes you stronger."
    else:
        return "🎯 Don't give up! Focus on the explanations. You've got this!"
