"""
Practice Service — Auto-generates quizzes from weak topics using deterministic topic_code matching.
Zero fuzzy logic in the hot path. All matching is exact WHERE topic_code = 'X'.
"""
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
    {"key": "computer_knowledge", "name": "Computer Knowledge", "icon": "desktop-outline", "color": "#8b5cf6"},
    {"key": "current_affairs", "name": "Current Affairs", "icon": "newspaper-outline", "color": "#ec4899"},
    {"key": "general_knowledge", "name": "General Knowledge", "icon": "school-outline", "color": "#84cc16"},
]

SUBJECT_KEY_MAP = {cat["key"]: cat["name"] for cat in QUIZ_CATEGORIES}


async def get_quiz_categories_with_counts(db: AsyncSession) -> list:
    result = []
    for cat in QUIZ_CATEGORIES:
        stmt = select(func.count(QuizQuestion.id)).where(
            func.lower(QuizQuestion.subject) == cat["name"].lower()
        )
        count = (await db.execute(stmt)).scalar() or 0
        result.append({**cat, "question_count": count, "has_questions": count > 0})
    return result


async def get_daily_quiz(db: AsyncSession, user_id: uuid.UUID, subject: str, limit: int = 10) -> list:
    canonical_subject = SUBJECT_KEY_MAP.get(subject.lower(), subject)
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())

    attempted_today = select(QuizAttempt.question_id).where(
        QuizAttempt.user_id == user_id, QuizAttempt.attempted_at >= today_start
    )

    stmt = (
        select(QuizQuestion)
        .where(func.lower(QuizQuestion.subject) == canonical_subject.lower(),
               QuizQuestion.id.not_in(attempted_today))
        .order_by(func.random()).limit(limit)
    )
    return [_serialize_quiz_question(q) for q in (await db.execute(stmt)).scalars().all()]


async def get_weak_topic_quiz(db: AsyncSession, user_id: uuid.UUID, limit: int = 10) -> dict:
    """
    Personalized quiz using DETERMINISTIC topic_code matching.
    1. Get user's weak topics (sorted by worst accuracy)
    2. For each weak topic, match quiz questions by topic_code (exact) or subject (fallback)
    3. Prioritize: unattempted → wrong → all, ordered EASY→MED→HARD
    """
    stmt = (
        select(UserWeakTopic)
        .where(UserWeakTopic.user_id == user_id, UserWeakTopic.accuracy < 60.0)
        .order_by(UserWeakTopic.accuracy.asc()).limit(5)
    )
    weak_topics = (await db.execute(stmt)).scalars().all()

    if not weak_topics:
        return {"questions": [], "weak_topics": [], "message": "No weak topics detected yet. Take a mock test first!"}

    # Get user's attempted + wrong question IDs
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

    for wt in weak_topics:
        # Resolve display name from topic_code
        display_info = None
        if wt.topic_code:
            display_info = await taxonomy_service.resolve_topic_code(db, wt.topic_code)

        display_subject = display_info["subject"] if display_info else wt.subject
        display_topic = display_info["topic"] if display_info else (wt.topic or "General")

        # Get mastery info
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

        per_topic = max(2, limit // len(weak_topics))
        topic_qs = await _fetch_prioritized_questions(
            db, wt.topic_code, display_subject, display_topic, per_topic, attempted_ids, wrong_ids
        )
        questions.extend(topic_qs)

    # Deduplicate
    seen = set()
    unique_qs = []
    for q in questions:
        if q.id not in seen:
            seen.add(q.id)
            unique_qs.append(q)

    return {
        "questions": [_serialize_quiz_question(q) for q in unique_qs[:limit]],
        "weak_topics": weak_topic_info,
        "total_available": await _count_weak_topic_questions(db, weak_topics),
        "message": f"Based on your mock test results, we found {len(weak_topic_info)} weak areas to improve."
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
        text_conditions = [func.lower(QuizQuestion.subject) == subject.lower()]
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
        subj_cond = [func.lower(QuizQuestion.subject) == subject.lower()]
        if existing:
            subj_cond.append(QuizQuestion.id.not_in(existing))
        fallback2 = (await db.execute(
            select(QuizQuestion).where(*subj_cond)
            .order_by(func.random()).limit(limit - len(result_qs))
        )).scalars().all()
        result_qs.extend(fallback2)

    return result_qs[:limit]


async def get_more_practice(db: AsyncSession, user_id: uuid.UUID, subject: str,
                            topic: Optional[str] = None, topic_code: Optional[str] = None,
                            exclude_ids: List[str] = [], limit: int = 10) -> dict:
    """Get more practice questions from the same topic."""
    exclude_uuids = [uuid.UUID(eid) for eid in exclude_ids if eid]

    # Primary: match by topic_code
    if topic_code:
        conditions = [QuizQuestion.topic_code == topic_code]
    else:
        conditions = [func.lower(QuizQuestion.subject) == subject.lower()]
        if topic:
            conditions.append(func.lower(QuizQuestion.topic) == topic.lower())

    if exclude_uuids:
        conditions.append(QuizQuestion.id.not_in(exclude_uuids))

    questions = (await db.execute(
        select(QuizQuestion).where(*conditions).order_by(func.random()).limit(limit)
    )).scalars().all()

    # Count remaining
    all_exclude = exclude_uuids + [q.id for q in questions]
    count_cond = [QuizQuestion.topic_code == topic_code] if topic_code else [func.lower(QuizQuestion.subject) == subject.lower()]
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
    correct = 0
    total = len(answers)
    details = []
    topic_stats = {}  # topic_code → {correct, total, subject, topic}

    for ans in answers:
        q_id = uuid.UUID(ans["question_id"])
        selected_index = ans.get("selected_option_index")

        question = (await db.execute(select(QuizQuestion).where(QuizQuestion.id == q_id))).scalars().first()

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

        db.add(QuizAttempt(user_id=user_id, question_id=q_id, was_correct=was_correct))

        if question:
            details.append({
                "question_id": str(q_id), "question_text": question.question_text,
                "was_correct": was_correct, "selected_option_index": selected_index,
                "correct_option_index": correct_index, "explanation": question.explanation or ""
            })

            # Track by topic_code (deterministic)
            tc = question.topic_code or f"__{question.subject}_{question.topic}"
            if tc not in topic_stats:
                topic_stats[tc] = {"correct": 0, "total": 0, "subject": question.subject,
                                   "topic": question.topic, "topic_code": question.topic_code}
            topic_stats[tc]["total"] += 1
            if was_correct:
                topic_stats[tc]["correct"] += 1

    await _update_streak(db, user_id)
    await db.commit()

    # Update mastery per topic
    for tc, stats in topic_stats.items():
        await _update_mastery(db, user_id, stats["subject"], stats["topic"],
                              stats["topic_code"], stats["correct"], stats["total"])

    user = (await db.execute(select(User).where(User.id == user_id))).scalars().first()
    
    # Gamification Logic
    points_earned = correct * 10
    old_stars = user.stars if user else 0
    new_star_unlocked = False
    new_stars = old_stars

    if user:
        user.points = (user.points or 0) + points_earned
        
        # Determine stars based on points
        total_points = user.points
        if total_points >= 5000: new_stars = 5
        elif total_points >= 2500: new_stars = 4
        elif total_points >= 1000: new_stars = 3
        elif total_points >= 500: new_stars = 2
        elif total_points >= 100: new_stars = 1
        
        if new_stars > old_stars:
            user.stars = new_stars
            new_star_unlocked = True
        
        db.add(user)

    await db.commit()

    accuracy = (correct / total * 100) if total > 0 else 0

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

    return {
        "total": total, "correct": correct, "incorrect": total - correct,
        "accuracy": round(accuracy, 1), "details": details,
        "encouragement": _get_encouragement(accuracy), "mastery": mastery_info,
        "points_earned": points_earned, "total_points": user.points if user else 0,
        "stars": user.stars if user else 0, "new_star_unlocked": new_star_unlocked
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
        accuracy = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        topic_code = stats["topic_code"]

        # Try to find existing by topic_code first, then by text
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
                    UserWeakTopic.subject == stats["subject"],
                    UserWeakTopic.topic == stats["topic"]
                )
            )).scalars().first()

        if existing:
            existing.total_questions += stats["total"]
            existing.correct_count += stats["correct"]
            existing.accuracy = (existing.correct_count / existing.total_questions * 100) if existing.total_questions > 0 else 0
            if topic_code and not existing.topic_code:
                existing.topic_code = topic_code  # Backfill code for legacy records
            db.add(existing)
        else:
            db.add(UserWeakTopic(
                user_id=user_id, subject=stats["subject"], topic=stats["topic"],
                topic_code=topic_code, accuracy=accuracy,
                total_questions=stats["total"], correct_count=stats["correct"]
            ))

    await db.commit()


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
            explanation=q.get("explanation", ""),
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
                func.lower(QuizQuestion.subject) == subject.lower(),
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
                func.lower(QuizQuestion.subject) == subject.lower(),
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


async def _count_weak_topic_questions(db, weak_topics) -> int:
    total = 0
    for wt in weak_topics:
        if wt.topic_code:
            count = (await db.execute(
                select(func.count(QuizQuestion.id)).where(QuizQuestion.topic_code == wt.topic_code)
            )).scalar() or 0
        else:
            conds = [func.lower(QuizQuestion.subject) == wt.subject.lower()]
            if wt.topic:
                conds.append(func.lower(QuizQuestion.topic) == wt.topic.lower())
            count = (await db.execute(select(func.count(QuizQuestion.id)).where(*conds))).scalar() or 0
        total += count
    return total


def _serialize_quiz_question(q: QuizQuestion) -> dict:
    return {
        "id": str(q.id), "question_text": q.question_text, "image_url": q.image_url,
        "subject": q.subject, "topic": q.topic, "topic_code": q.topic_code,
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
