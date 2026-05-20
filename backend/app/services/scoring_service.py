import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.attempt import Attempt, AttemptStatus
from app.models.user_answer import UserAnswer
from app.models.test_series import TestSeries, TestType
from app.models.question import Question
from app.models.section import Section
from app.models.result import Result
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.models.enrollment import Enrollment
from app.schemas.attempt_schema import UserAnswerCreate
from app.services import entitlement_service
from datetime import datetime
from typing import List

async def get_user_attempts(db: AsyncSession, user_id: uuid.UUID) -> List[dict]:
    stmt = (
        select(Attempt)
        .options(selectinload(Attempt.test_series))
        .where(Attempt.user_id == user_id)
        .order_by(Attempt.started_at.desc())
    )
    result = await db.execute(stmt)
    attempts = result.scalars().all()
    return [
        {
            "id": a.id,
            "user_id": a.user_id,
            "test_series_id": a.test_series_id,
            "started_at": a.started_at,
            "ended_at": a.ended_at,
            "status": a.status,
            "test_title": a.test_series.title if a.test_series else None,
        }
        for a in attempts
    ]

async def start_attempt(db: AsyncSession, user_id: uuid.UUID, test_id: uuid.UUID) -> dict:
    # First check if active attempt exists
    stmt = select(Attempt).options(selectinload(Attempt.test_series)).where(
        Attempt.user_id == user_id, 
        Attempt.test_series_id == test_id,
        Attempt.status == AttemptStatus.IN_PROGRESS
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return {
            "id": existing.id,
            "user_id": existing.user_id,
            "test_series_id": existing.test_series_id,
            "started_at": existing.started_at,
            "ended_at": existing.ended_at,
            "status": existing.status,
            "test_title": existing.test_series.title if existing.test_series else None,
            "test_series": {
                "cdn_url": existing.test_series.cdn_url if existing.test_series else None,
                "total_duration_minutes": existing.test_series.total_duration_minutes if existing.test_series else None,
                "has_sectional_timing": bool(existing.test_series.has_sectional_timing) if existing.test_series else False,
                "negative_marking": existing.test_series.negative_marking if existing.test_series else 0.25,
            },
        }
        
    # VALIDATION: two gates run in order.
    # Gate A — exam_stage pricing (NEW path): PYQ always allowed, MOCK under
    # a priced stage requires an active purchase. If this gate returns, fall
    # through to Gate B (legacy folder/enrollment) so old free courses keep
    # working. Gate A raises 402 on a paid stage with no entitlement — that's
    # the signal the frontend turns into a checkout redirect.
    ts_stmt = select(TestSeries).where(TestSeries.id == test_id)
    ts_res = await db.execute(ts_stmt)
    test_series = ts_res.scalars().first()
    if test_series is None:
        raise HTTPException(status_code=404, detail="Test series not found")

    await entitlement_service.ensure_test_series_access(db, user_id, test_series)

    # Short-circuit: PYQs and test_series bound to a free, priced-0 stage
    # already passed Gate A. We skip the legacy course-enrollment gate in
    # those cases so PYQs never accidentally require an enrollment.
    if test_series.test_type == TestType.PYQ:
        attempt = Attempt(user_id=user_id, test_series_id=test_id)
        db.add(attempt)
        await db.commit()
        stmt = select(Attempt).options(selectinload(Attempt.test_series)).where(Attempt.id == attempt.id)
        attempt_full = (await db.execute(stmt)).scalars().first()
        return {
            "id": attempt_full.id,
            "user_id": attempt_full.user_id,
            "test_series_id": attempt_full.test_series_id,
            "started_at": attempt_full.started_at,
            "ended_at": attempt_full.ended_at,
            "status": attempt_full.status,
            "test_title": attempt_full.test_series.title if attempt_full.test_series else None,
            "test_series": {
                "cdn_url": attempt_full.test_series.cdn_url if attempt_full.test_series else None,
                "total_duration_minutes": attempt_full.test_series.total_duration_minutes if attempt_full.test_series else None,
                "has_sectional_timing": bool(attempt_full.test_series.has_sectional_timing) if attempt_full.test_series else False,
                "negative_marking": attempt_full.test_series.negative_marking if attempt_full.test_series else 0.25,
            },
        }

    if test_series.exam_stage_id is not None:
        # Stage access already validated in Gate A (either free or purchased).
        attempt = Attempt(user_id=user_id, test_series_id=test_id)
        db.add(attempt)
        await db.commit()
        stmt = select(Attempt).options(selectinload(Attempt.test_series)).where(Attempt.id == attempt.id)
        attempt_full = (await db.execute(stmt)).scalars().first()
        return {
            "id": attempt_full.id,
            "user_id": attempt_full.user_id,
            "test_series_id": attempt_full.test_series_id,
            "started_at": attempt_full.started_at,
            "ended_at": attempt_full.ended_at,
            "status": attempt_full.status,
            "test_title": attempt_full.test_series.title if attempt_full.test_series else None,
            "test_series": {
                "cdn_url": attempt_full.test_series.cdn_url if attempt_full.test_series else None,
                "total_duration_minutes": attempt_full.test_series.total_duration_minutes if attempt_full.test_series else None,
                "has_sectional_timing": bool(attempt_full.test_series.has_sectional_timing) if attempt_full.test_series else False,
                "negative_marking": attempt_full.test_series.negative_marking if attempt_full.test_series else 0.25,
            },
        }

    # Gate B — legacy folder/enrollment path for old course-linked tests.
    stmt = (
        select(FolderTest)
        .options(selectinload(FolderTest.folder))
        .where(FolderTest.test_id == test_id)
    )
    result = await db.execute(stmt)
    folder_test_links = result.scalars().all()

    has_access = False
    
    # If the test is completely unlinked to any course, we might want to either block it or allow it.
    # We will block it unless they are an admin, but for now let's assume if it's not in a folder, it's NOT a public test.
    if not folder_test_links:
        pass # Not accessible

    for link in folder_test_links:
        if link.folder and getattr(link.folder, 'is_free', False):
            has_access = True
            break
            
        # Check enrollment for the course containing this folder
        if link.folder:
            course_id = getattr(link.folder, 'course_id', None)
            if course_id:
                enrollment_stmt = select(Enrollment).where(
                    Enrollment.user_id == user_id,
                    Enrollment.course_id == course_id
                )
                enrollment_res = await db.execute(enrollment_stmt)
                if enrollment_res.scalars().first():
                    has_access = True
                    break

    if not has_access:
        raise HTTPException(status_code=403, detail="You must enroll in the course to access this test.")

    attempt = Attempt(user_id=user_id, test_series_id=test_id)
    db.add(attempt)
    await db.commit()
    
    # Eager load the test series exactly as get_user_attempts does
    stmt = select(Attempt).options(selectinload(Attempt.test_series)).where(Attempt.id == attempt.id)
    attempt_res = await db.execute(stmt)
    attempt_full = attempt_res.scalars().first()
    
    # Bundle the Pydantic schema return
    return {
        "id": attempt_full.id,
        "user_id": attempt_full.user_id,
        "test_series_id": attempt_full.test_series_id,
        "started_at": attempt_full.started_at,
        "ended_at": attempt_full.ended_at,
        "status": attempt_full.status,
        "test_title": attempt_full.test_series.title if attempt_full.test_series else None,
        "test_series": {
            "cdn_url": attempt_full.test_series.cdn_url if attempt_full.test_series else None,
            "total_duration_minutes": attempt_full.test_series.total_duration_minutes if attempt_full.test_series else None,
            "has_sectional_timing": bool(attempt_full.test_series.has_sectional_timing) if attempt_full.test_series else False,
            "negative_marking": attempt_full.test_series.negative_marking if attempt_full.test_series else 0.25,
        },
    }

async def get_attempt_answers(db: AsyncSession, attempt_id: uuid.UUID, user_id: uuid.UUID) -> List[UserAnswer]:
    """Get all saved answers for an attempt (used to resume a paused test)."""
    # Verify attempt belongs to user
    attempt_stmt = select(Attempt).where(Attempt.id == attempt_id, Attempt.user_id == user_id)
    attempt_res = await db.execute(attempt_stmt)
    attempt = attempt_res.scalars().first()
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    
    stmt = select(UserAnswer).where(UserAnswer.attempt_id == attempt_id)
    result = await db.execute(stmt)
    return result.scalars().all()

async def save_answer(db: AsyncSession, attempt_id: uuid.UUID, answer_in: UserAnswerCreate) -> UserAnswer:
    # Upsert logic for answer
    stmt = select(UserAnswer).where(
        UserAnswer.attempt_id == attempt_id,
        UserAnswer.question_id == answer_in.question_id
    )
    result = await db.execute(stmt)
    existing_answer = result.scalars().first()
    
    if existing_answer:
        existing_answer.selected_option_index = answer_in.selected_option_index
        existing_answer.time_spent_seconds += answer_in.time_spent_seconds
        db.add(existing_answer)
        await db.commit()
        await db.refresh(existing_answer)
        return existing_answer
        
    new_answer = UserAnswer(attempt_id=attempt_id, **answer_in.model_dump())
    db.add(new_answer)
    await db.commit()
    await db.refresh(new_answer)
    return new_answer

async def submit_attempt(db: AsyncSession, attempt_id: uuid.UUID) -> Result:
    # Eager-load test_series only (for negative_marking). Sections are no
    # longer pulled here — the per-Q marks come from each answer's
    # question.section join below, so loading every section unnecessarily
    # padded the response and slowed submit on long papers.
    attempt = (await db.execute(
        select(Attempt)
        .options(selectinload(Attempt.test_series))
        .where(Attempt.id == attempt_id)
    )).scalars().first()
    if not attempt or attempt.status == AttemptStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Invalid attempt or already submitted")
        
    attempt.status = AttemptStatus.SUBMITTED
    attempt.ended_at = datetime.utcnow()
    
    # Fetch all answers for this attempt
    answers_stmt = select(UserAnswer).options(
        selectinload(UserAnswer.question).selectinload(Question.section)
    ).where(UserAnswer.attempt_id == attempt_id)
    answers = (await db.execute(answers_stmt)).scalars().all()
    
    total_score = 0.0
    correct = 0
    incorrect = 0
    skipped = 0
    
    test_series = attempt.test_series
    neg_mark = test_series.negative_marking if test_series else 0.25

    for ans in answers:
        q_section = ans.question.section if ans.question else None
        marks = q_section.marks_per_question if q_section else 1.0
        
        if ans.selected_option_index is not None:
            # check correctness using JSONB
            try:
                selected_opt = ans.question.options[ans.selected_option_index]
                if selected_opt.get("is_correct", False):
                    correct += 1
                    total_score += marks
                else:
                    incorrect += 1
                    total_score -= neg_mark
            except (IndexError, TypeError):
                incorrect += 1
                total_score -= neg_mark
        else:
            skipped += 1
            
    total_q_answered = correct + incorrect
    accuracy = (correct / total_q_answered * 100) if total_q_answered > 0 else 0.0
    result = Result(
        attempt_id=attempt_id,
        total_score=total_score,
        correct_count=correct,
        incorrect_count=incorrect,
        skipped_count=skipped,
        accuracy_percentage=accuracy,
    )
    db.add(result)
    await db.flush()  # flush to assign an ID and evaluate

    # Rank/percentile via SQL aggregates — never load every Result row into
    # memory. With thousands of attempts on a popular PYQ that scan dominated
    # submit latency.
    from sqlalchemy import func as _sql_func
    base_filter = (
        Attempt.test_series_id == attempt.test_series_id,
        Attempt.status == AttemptStatus.SUBMITTED,
    )
    higher_scores = (await db.execute(
        select(_sql_func.count(Result.id))
        .join(Attempt, Attempt.id == Result.attempt_id)
        .where(*base_filter, Result.total_score > total_score)
    )).scalar_one()
    total_candidates = (await db.execute(
        select(_sql_func.count(Result.id))
        .join(Attempt, Attempt.id == Result.attempt_id)
        .where(*base_filter)
    )).scalar_one()

    rank = higher_scores + 1
    if total_candidates > 1:
        percentile = ((total_candidates - rank) / total_candidates) * 100
    else:
        percentile = 100.0

    result.rank = rank
    result.percentile = round(percentile, 2)

    db.add(result)
    db.add(attempt)
    await db.commit()
    await db.refresh(result)
    
    # Auto-update user's weak topics for adaptive practice quizzes
    try:
        from app.services.practice_service import update_weak_topics_from_attempt
        await update_weak_topics_from_attempt(db, attempt.user_id, attempt_id)
    except Exception as e:
        print(f"[WeakTopics] Failed to update weak topics: {e}")
    
    return result
