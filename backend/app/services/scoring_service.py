import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.attempt import Attempt, AttemptStatus
from app.models.user_answer import UserAnswer
from app.models.test_series import TestSeries
from app.models.question import Question
from app.models.option import Option
from app.models.result import Result
from app.schemas.attempt_schema import UserAnswerCreate
from datetime import datetime
from typing import List

async def get_user_attempts(db: AsyncSession, user_id: uuid.UUID) -> List[Attempt]:
    stmt = select(Attempt).where(Attempt.user_id == user_id).order_by(Attempt.started_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()

async def start_attempt(db: AsyncSession, user_id: uuid.UUID, test_id: uuid.UUID) -> Attempt:
    # First check if active attempt exists
    stmt = select(Attempt).where(
        Attempt.user_id == user_id, 
        Attempt.test_series_id == test_id,
        Attempt.status == AttemptStatus.IN_PROGRESS
    )
    result = await db.execute(stmt)
    existing = result.scalars().first()
    if existing:
        return existing
        
    attempt = Attempt(user_id=user_id, test_series_id=test_id)
    db.add(attempt)
    await db.commit()
    await db.refresh(attempt)
    return attempt

async def save_answer(db: AsyncSession, attempt_id: uuid.UUID, answer_in: UserAnswerCreate) -> UserAnswer:
    # Upsert logic for answer
    stmt = select(UserAnswer).where(
        UserAnswer.attempt_id == attempt_id,
        UserAnswer.question_id == answer_in.question_id
    )
    result = await db.execute(stmt)
    existing_answer = result.scalars().first()
    
    if existing_answer:
        existing_answer.selected_option_id = answer_in.selected_option_id
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
    stmt = select(Attempt).options(
        selectinload(Attempt.test_series).selectinload(TestSeries.sections).selectinload(Section.questions).selectinload(Question.options),
        selectinload(Attempt.user_answers)
    ).where(Attempt.id == attempt_id)
    
    # In a real app we'd need more robust joins to fetch all questions for the exact test
    # Simplified calculation for demonstration
    attempt = (await db.execute(select(Attempt).where(Attempt.id == attempt_id))).scalars().first()
    if not attempt or attempt.status == AttemptStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Invalid attempt or already submitted")
        
    attempt.status = AttemptStatus.SUBMITTED
    attempt.ended_at = datetime.utcnow()
    
    # Fetch all answers for this attempt
    answers_stmt = select(UserAnswer).options(
        selectinload(UserAnswer.question).selectinload(Question.options)
    ).where(UserAnswer.attempt_id == attempt_id)
    answers = (await db.execute(answers_stmt)).scalars().all()
    
    # Needs actual scoring logic linking with test negative marking
    total_score = 0.0
    correct = 0
    incorrect = 0
    skipped = 0
    # Dummy scoring calculation 
    for ans in answers:
        if ans.selected_option_id:
            # check correctness
            correct_opt = next((o for o in ans.question.options if o.is_correct), None)
            if correct_opt and ans.selected_option_id == correct_opt.id:
                correct += 1
                total_score += 1.0 # assume 1 mark per question
            else:
                incorrect += 1
                total_score -= 0.25 # assume 0.25 negative marks
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
    db.add(attempt)
    await db.commit()
    await db.refresh(result)
    return result
