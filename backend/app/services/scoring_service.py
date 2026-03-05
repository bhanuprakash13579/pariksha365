import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.attempt import Attempt, AttemptStatus
from app.models.user_answer import UserAnswer
from app.models.test_series import TestSeries
from app.models.question import Question
from app.models.section import Section
from app.models.result import Result
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.models.enrollment import Enrollment
from app.schemas.attempt_schema import UserAnswerCreate
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
                "cdn_url": existing.test_series.cdn_url if existing.test_series else None
            }
        }
        
    # VALIDATION: Check if test is free or if user is enrolled
    # 1. Find the folder this test is in
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
            "cdn_url": attempt_full.test_series.cdn_url if attempt_full.test_series else None
        }
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
    # Eager-load test_series (for negative marking) and user_answers with question+options+section
    attempt = (await db.execute(
        select(Attempt)
        .options(
            selectinload(Attempt.test_series).selectinload(TestSeries.sections),
        )
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

    # Calculate rank and percentile
    other_results_stmt = select(Result).join(Attempt).where(
        Attempt.test_series_id == attempt.test_series_id,
        Attempt.status == AttemptStatus.SUBMITTED
    )
    other_results_q = await db.execute(other_results_stmt)
    all_results = other_results_q.scalars().all()
    
    # rank = 1 + number of people with strictly higher score
    higher_scores = sum(1 for r in all_results if r.total_score > total_score)
    rank = higher_scores + 1
    
    total_candidates = len(all_results)
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
