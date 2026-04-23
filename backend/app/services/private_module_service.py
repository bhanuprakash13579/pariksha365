"""Private-module service — isolated quiz universe (EPFO APFC etc.).

Scoping rule: every query is filtered by ``module_id`` so EPFO performance
never triggers non-EPFO suggestions and vice-versa.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException

from app.models.private_module import (
    PrivateModule, PrivateModuleQuestion, PrivateModuleAccess,
    PrivateModuleAttempt, PrivateModuleWeakTopic,
)


# ──────────────── Access control ────────────────

def _norm(email: Optional[str]) -> Optional[str]:
    return email.strip().lower() if email else None


async def user_has_access(db: AsyncSession, user_email: str, module_id: uuid.UUID) -> bool:
    email = _norm(user_email)
    if not email:
        return False
    stmt = select(PrivateModuleAccess.id).where(
        PrivateModuleAccess.module_id == module_id,
        func.lower(PrivateModuleAccess.email) == email,
    )
    return (await db.execute(stmt)).scalars().first() is not None


async def list_accessible_modules(db: AsyncSession, user_email: str) -> list[PrivateModule]:
    """All active modules that this user's email has been granted access to."""
    email = _norm(user_email)
    if not email:
        return []
    stmt = (
        select(PrivateModule)
        .join(PrivateModuleAccess, PrivateModuleAccess.module_id == PrivateModule.id)
        .where(
            PrivateModule.is_active.is_(True),
            func.lower(PrivateModuleAccess.email) == email,
        )
        .order_by(PrivateModule.name.asc())
    )
    return list((await db.execute(stmt)).scalars().all())


async def get_module_by_slug(db: AsyncSession, slug: str) -> Optional[PrivateModule]:
    stmt = select(PrivateModule).where(PrivateModule.slug == slug,
                                       PrivateModule.is_active.is_(True))
    return (await db.execute(stmt)).scalars().first()


async def require_module_access(db: AsyncSession, user_email: str, slug: str) -> PrivateModule:
    module = await get_module_by_slug(db, slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    if not await user_has_access(db, user_email, module.id):
        raise HTTPException(status_code=403, detail="Access denied to this module")
    return module


# ──────────────── Serialisation ────────────────

def serialize_question(q: PrivateModuleQuestion) -> dict:
    return {
        "id": str(q.id),
        "question_text": q.question_text,
        "options": q.options or [],
        "explanation": q.explanation or "",
        "subject": q.subject,
        "topic": q.topic,
        "topic_code": q.topic_code,
        "difficulty": q.difficulty,
    }


# ──────────────── Subject & topic listings ────────────────

async def module_subject_summary(db: AsyncSession, module_id: uuid.UUID,
                                 user_id: uuid.UUID) -> list[dict]:
    """Per-subject question counts + how many the user has already attempted."""
    counts_stmt = (
        select(PrivateModuleQuestion.subject, func.count(PrivateModuleQuestion.id))
        .where(PrivateModuleQuestion.module_id == module_id)
        .group_by(PrivateModuleQuestion.subject)
    )
    counts = {row[0]: row[1] for row in (await db.execute(counts_stmt)).all()}

    # Attempted counts per subject
    attempted_stmt = (
        select(PrivateModuleQuestion.subject, func.count(func.distinct(PrivateModuleAttempt.question_id)))
        .join(PrivateModuleAttempt, PrivateModuleAttempt.question_id == PrivateModuleQuestion.id)
        .where(
            PrivateModuleQuestion.module_id == module_id,
            PrivateModuleAttempt.user_id == user_id,
        )
        .group_by(PrivateModuleQuestion.subject)
    )
    attempted = {row[0]: row[1] for row in (await db.execute(attempted_stmt)).all()}

    summary = []
    for subject, total in sorted(counts.items(), key=lambda kv: -kv[1]):
        summary.append({
            "subject": subject,
            "question_count": total,
            "attempted_count": attempted.get(subject, 0),
        })
    return summary


async def module_topic_summary(db: AsyncSession, module_id: uuid.UUID,
                               subject: str) -> list[dict]:
    stmt = (
        select(PrivateModuleQuestion.topic,
               PrivateModuleQuestion.topic_code,
               func.count(PrivateModuleQuestion.id))
        .where(PrivateModuleQuestion.module_id == module_id,
               PrivateModuleQuestion.subject == subject)
        .group_by(PrivateModuleQuestion.topic, PrivateModuleQuestion.topic_code)
        .order_by(func.count(PrivateModuleQuestion.id).desc())
    )
    return [
        {"topic": row[0], "topic_code": row[1], "question_count": row[2]}
        for row in (await db.execute(stmt)).all()
    ]


# ──────────────── Question fetchers ────────────────

async def get_daily_quiz(db: AsyncSession, module_id: uuid.UUID, user_id: uuid.UUID,
                         subject: str, limit: int = 10) -> list[dict]:
    """Random unattempted-today questions from a given subject within the module."""
    today_start = datetime.combine(datetime.utcnow().date(), datetime.min.time())
    attempted_today = select(PrivateModuleAttempt.question_id).where(
        PrivateModuleAttempt.user_id == user_id,
        PrivateModuleAttempt.module_id == module_id,
        PrivateModuleAttempt.attempted_at >= today_start,
    )
    stmt = (
        select(PrivateModuleQuestion)
        .where(
            PrivateModuleQuestion.module_id == module_id,
            PrivateModuleQuestion.subject == subject,
            PrivateModuleQuestion.id.not_in(attempted_today),
        )
        .order_by(func.random())
        .limit(limit)
    )
    return [serialize_question(q) for q in (await db.execute(stmt)).scalars().all()]


async def get_more_practice(db: AsyncSession, module_id: uuid.UUID, user_id: uuid.UUID,
                            subject: str, topic: Optional[str],
                            exclude_ids: list[str], limit: int = 10) -> list[dict]:
    exclude_uuids = []
    for eid in exclude_ids:
        try:
            exclude_uuids.append(uuid.UUID(eid))
        except Exception:
            pass

    conditions = [
        PrivateModuleQuestion.module_id == module_id,
        PrivateModuleQuestion.subject == subject,
    ]
    if topic:
        conditions.append(PrivateModuleQuestion.topic == topic)
    if exclude_uuids:
        conditions.append(PrivateModuleQuestion.id.not_in(exclude_uuids))

    stmt = (
        select(PrivateModuleQuestion)
        .where(*conditions)
        .order_by(func.random())
        .limit(limit)
    )
    return [serialize_question(q) for q in (await db.execute(stmt)).scalars().all()]


async def get_weak_topic_quiz(db: AsyncSession, module_id: uuid.UUID,
                              user_id: uuid.UUID, limit: int = 10) -> dict:
    """Return questions from the user's weakest topic_codes within THIS module.

    Falls back to a balanced unattempted mix if the user has no module-scoped
    weak-topic signal yet, so the page is never empty on first visit.
    """
    weak_stmt = (
        select(PrivateModuleWeakTopic)
        .where(
            PrivateModuleWeakTopic.user_id == user_id,
            PrivateModuleWeakTopic.module_id == module_id,
            PrivateModuleWeakTopic.accuracy < 60.0,
            PrivateModuleWeakTopic.total_questions >= 2,
        )
        .order_by(PrivateModuleWeakTopic.accuracy.asc())
        .limit(5)
    )
    weak = list((await db.execute(weak_stmt)).scalars().all())

    attempted_ids = set(r[0] for r in (await db.execute(
        select(PrivateModuleAttempt.question_id).where(
            PrivateModuleAttempt.user_id == user_id,
            PrivateModuleAttempt.module_id == module_id,
        )
    )).all())

    questions: list[dict] = []
    weak_info: list[dict] = []
    seen_ids: set = set()

    if weak:
        per_topic = max(2, limit // len(weak))
        for wt in weak:
            stmt = (
                select(PrivateModuleQuestion)
                .where(
                    PrivateModuleQuestion.module_id == module_id,
                    PrivateModuleQuestion.topic_code == wt.topic_code,
                    PrivateModuleQuestion.id.not_in(attempted_ids) if attempted_ids else sa_true(),
                )
                .order_by(func.random())
                .limit(per_topic)
            )
            topic_qs = list((await db.execute(stmt)).scalars().all())
            for q in topic_qs:
                if q.id not in seen_ids:
                    seen_ids.add(q.id)
                    questions.append(serialize_question(q))
            weak_info.append({
                "subject": wt.subject,
                "topic": wt.topic,
                "topic_code": wt.topic_code,
                "accuracy": round(wt.accuracy, 1),
                "total_attempted": wt.total_questions,
            })

    # Fallback: top up with random unattempted from the whole module.
    if len(questions) < limit:
        needed = limit - len(questions)
        stmt = (
            select(PrivateModuleQuestion)
            .where(
                PrivateModuleQuestion.module_id == module_id,
                PrivateModuleQuestion.id.not_in(seen_ids | attempted_ids)
                if (seen_ids | attempted_ids) else sa_true(),
            )
            .order_by(func.random())
            .limit(needed)
        )
        for q in (await db.execute(stmt)).scalars().all():
            questions.append(serialize_question(q))

    return {"questions": questions, "weak_topics": weak_info, "count": len(questions)}


def sa_true():
    """Helper for SQLAlchemy truthy condition."""
    from sqlalchemy import literal
    return literal(True)


# ──────────────── Submit + weak-topic update ────────────────

async def submit_answers(db: AsyncSession, module_id: uuid.UUID, user_id: uuid.UUID,
                         answers: list[dict]) -> dict:
    """Persist attempts, return scorecard, and update module-scoped weak topics."""
    correct_total = 0
    per_topic: dict[str, dict] = {}  # topic_code -> {subject, topic, tot, cor}
    scored = []

    for ans in answers:
        try:
            qid = uuid.UUID(ans.get("question_id"))
        except Exception:
            continue
        q = (await db.execute(
            select(PrivateModuleQuestion).where(
                PrivateModuleQuestion.id == qid,
                PrivateModuleQuestion.module_id == module_id,
            )
        )).scalars().first()
        if not q:
            continue

        selected_idx = ans.get("selected_option_index")
        is_correct = False
        if selected_idx is not None and isinstance(q.options, list):
            if 0 <= selected_idx < len(q.options):
                is_correct = bool(q.options[selected_idx].get("is_correct"))

        db.add(PrivateModuleAttempt(
            user_id=user_id, module_id=module_id, question_id=qid, was_correct=is_correct,
        ))
        if is_correct:
            correct_total += 1

        t = per_topic.setdefault(q.topic_code, {"subject": q.subject, "topic": q.topic,
                                                "tot": 0, "cor": 0})
        t["tot"] += 1
        if is_correct:
            t["cor"] += 1

        scored.append({
            "question_id": str(qid),
            "was_correct": is_correct,
            "correct_option_index": next((i for i, o in enumerate(q.options or [])
                                          if o.get("is_correct")), None),
            "explanation": q.explanation,
        })

    # Update per-topic weak-topic tracker
    for topic_code, agg in per_topic.items():
        wt = (await db.execute(
            select(PrivateModuleWeakTopic).where(
                PrivateModuleWeakTopic.user_id == user_id,
                PrivateModuleWeakTopic.module_id == module_id,
                PrivateModuleWeakTopic.topic_code == topic_code,
            )
        )).scalars().first()

        if wt is None:
            wt = PrivateModuleWeakTopic(
                user_id=user_id,
                module_id=module_id,
                subject=agg["subject"],
                topic=agg["topic"],
                topic_code=topic_code,
                total_questions=agg["tot"],
                correct_count=agg["cor"],
                accuracy=(agg["cor"] / agg["tot"]) * 100.0 if agg["tot"] else 0.0,
            )
            db.add(wt)
        else:
            wt.total_questions += agg["tot"]
            wt.correct_count += agg["cor"]
            wt.accuracy = (wt.correct_count / wt.total_questions) * 100.0 \
                if wt.total_questions else 0.0
            wt.subject = agg["subject"]
            wt.topic = agg["topic"]

    await db.commit()

    total = len(scored)
    return {
        "total_questions": total,
        "correct": correct_total,
        "wrong": total - correct_total,
        "score_pct": round((correct_total / total) * 100, 1) if total else 0.0,
        "results": scored,
    }


# ──────────────── Admin: access-list CRUD ────────────────

async def list_access(db: AsyncSession, module_id: uuid.UUID) -> list[dict]:
    stmt = (
        select(PrivateModuleAccess)
        .where(PrivateModuleAccess.module_id == module_id)
        .order_by(PrivateModuleAccess.granted_at.desc())
    )
    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(r.id),
            "email": r.email,
            "note": r.note,
            "granted_by": str(r.granted_by) if r.granted_by else None,
            "granted_at": r.granted_at.isoformat() if r.granted_at else None,
        }
        for r in rows
    ]


async def grant_access(db: AsyncSession, module_id: uuid.UUID, email: str,
                       note: Optional[str], granted_by: Optional[uuid.UUID]) -> dict:
    email = _norm(email)
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email required")

    existing = (await db.execute(
        select(PrivateModuleAccess).where(
            PrivateModuleAccess.module_id == module_id,
            func.lower(PrivateModuleAccess.email) == email,
        )
    )).scalars().first()
    if existing:
        return {"id": str(existing.id), "email": existing.email, "status": "already_granted"}

    row = PrivateModuleAccess(module_id=module_id, email=email, note=note,
                              granted_by=granted_by)
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": str(row.id), "email": row.email, "status": "granted"}


async def revoke_access(db: AsyncSession, module_id: uuid.UUID, access_id: uuid.UUID) -> dict:
    row = (await db.execute(
        select(PrivateModuleAccess).where(
            PrivateModuleAccess.id == access_id,
            PrivateModuleAccess.module_id == module_id,
        )
    )).scalars().first()
    if not row:
        raise HTTPException(status_code=404, detail="Access entry not found")
    await db.delete(row)
    await db.commit()
    return {"status": "revoked", "id": str(access_id)}


async def list_all_modules(db: AsyncSession) -> list[dict]:
    stmt = select(PrivateModule).order_by(PrivateModule.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    result = []
    for m in rows:
        q_count_stmt = select(func.count(PrivateModuleQuestion.id)).where(
            PrivateModuleQuestion.module_id == m.id
        )
        a_count_stmt = select(func.count(PrivateModuleAccess.id)).where(
            PrivateModuleAccess.module_id == m.id
        )
        q_count = (await db.execute(q_count_stmt)).scalar() or 0
        a_count = (await db.execute(a_count_stmt)).scalar() or 0
        result.append({
            "id": str(m.id),
            "slug": m.slug,
            "name": m.name,
            "description": m.description,
            "is_active": m.is_active,
            "question_count": q_count,
            "granted_count": a_count,
        })
    return result
