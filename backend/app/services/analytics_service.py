import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException
from app.models.attempt import Attempt, AttemptStatus
from app.models.user_answer import UserAnswer
from app.models.course import Course
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.schemas.analytics_schema import SubjectPerformance, AttemptAnalyticsResponse, SeriesAnalyticsResponse

async def get_attempt_analytics(db: AsyncSession, attempt_id: uuid.UUID, user_id: uuid.UUID) -> AttemptAnalyticsResponse:
    stmt = (
        select(Attempt)
        .options(
            selectinload(Attempt.user_answers).selectinload(UserAnswer.question),
            selectinload(Attempt.user_answers).selectinload(UserAnswer.selected_option),
            selectinload(Attempt.result)
        )
        .where(Attempt.id == attempt_id, Attempt.user_id == user_id)
    )
    result = await db.execute(stmt)
    attempt = result.scalars().first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
        
    if attempt.status != AttemptStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Attempt is not submitted yet")
        
    subject_map = {}
    
    for ans in attempt.user_answers:
        subj = ans.question.subject or "General"
        if subj not in subject_map:
            subject_map[subj] = {
                "total": 0, "correct": 0, "incorrect": 0, "skipped": 0, "time": 0
            }
        
        subject_map[subj]["total"] += 1
        subject_map[subj]["time"] += (ans.time_spent_seconds or 0)
        
        if not ans.selected_option_id:
            subject_map[subj]["skipped"] += 1
        else:
            if ans.selected_option and ans.selected_option.is_correct:
                subject_map[subj]["correct"] += 1
            else:
                subject_map[subj]["incorrect"] += 1
                
    performances = []
    for subj, stats in subject_map.items():
        acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        performances.append(SubjectPerformance(
            subject=subj,
            total_questions=stats["total"],
            correct=stats["correct"],
            incorrect=stats["incorrect"],
            skipped=stats["skipped"],
            accuracy_percentage=round(acc, 2),
            time_spent_seconds=stats["time"]
        ))
        
    total_score = attempt.result.total_score if attempt.result else 0.0
        
    return AttemptAnalyticsResponse(
        attempt_id=str(attempt.id),
        total_score=total_score,
        subject_performances=performances
    )

async def get_series_analytics(db: AsyncSession, course_id: uuid.UUID, user_id: uuid.UUID) -> SeriesAnalyticsResponse:
    stmt = (
        select(Course)
        .options(
            selectinload(Course.folders).selectinload(CourseFolder.tests)
        )
        .where(Course.id == course_id)
    )
    res = await db.execute(stmt)
    course = res.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    test_ids = []
    for f in course.folders:
        for t in f.tests:
            test_ids.append(t.test_id)
            
    if not test_ids:
        return SeriesAnalyticsResponse(course_id=str(course_id), total_attempts=0, average_score=0.0, subject_performances=[])
        
    stmt = (
        select(Attempt)
        .options(
            selectinload(Attempt.user_answers).selectinload(UserAnswer.question),
            selectinload(Attempt.user_answers).selectinload(UserAnswer.selected_option),
            selectinload(Attempt.result)
        )
        .where(Attempt.user_id == user_id, Attempt.test_series_id.in_(test_ids), Attempt.status == AttemptStatus.SUBMITTED)
    )
    res = await db.execute(stmt)
    attempts = res.scalars().unique().all()
    
    if not attempts:
        return SeriesAnalyticsResponse(course_id=str(course_id), total_attempts=0, average_score=0.0, subject_performances=[])
        
    total_score_sum = sum(a.result.total_score for a in attempts if a.result)
    avg_score = total_score_sum / len(attempts)
    
    subject_map = {}
    for attempt in attempts:
        for ans in attempt.user_answers:
            subj = ans.question.subject or "General"
            if subj not in subject_map:
                subject_map[subj] = {
                    "total": 0, "correct": 0, "incorrect": 0, "skipped": 0, "time": 0
                }
            
            subject_map[subj]["total"] += 1
            subject_map[subj]["time"] += (ans.time_spent_seconds or 0)
            
            if not ans.selected_option_id:
                subject_map[subj]["skipped"] += 1
            else:
                if ans.selected_option and ans.selected_option.is_correct:
                    subject_map[subj]["correct"] += 1
                else:
                    subject_map[subj]["incorrect"] += 1
                    
    performances = []
    for subj, stats in subject_map.items():
        acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        performances.append(SubjectPerformance(
            subject=subj,
            total_questions=stats["total"],
            correct=stats["correct"],
            incorrect=stats["incorrect"],
            skipped=stats["skipped"],
            accuracy_percentage=round(acc, 2),
            time_spent_seconds=stats["time"]
        ))
        
    return SeriesAnalyticsResponse(
        course_id=str(course_id),
        total_attempts=len(attempts),
        average_score=round(avg_score, 2),
        subject_performances=performances
    )
