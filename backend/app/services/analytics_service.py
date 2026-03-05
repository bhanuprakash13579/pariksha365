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
from app.schemas.analytics_schema import SubjectPerformance, TopicPerformance, AttemptAnalyticsResponse, SeriesAnalyticsResponse

# --- Helper: Build subject+topic performance map from answers ---
def _build_performance_map(answers):
    """Build a nested subject -> topic performance map from user answers, including time breakdowns."""
    subject_map = {}
    
    for ans in answers:
        subj = ans.question.subject or "General"
        topic = ans.question.topic or "General"
        time_s = ans.time_spent_seconds or 0
        
        if subj not in subject_map:
            subject_map[subj] = {
                "total": 0, "correct": 0, "incorrect": 0, "skipped": 0, "time": 0,
                "time_correct": 0, "time_incorrect": 0, "time_skipped": 0,
                "topics": {}
            }
        
        if topic not in subject_map[subj]["topics"]:
            subject_map[subj]["topics"][topic] = {
                "total": 0, "correct": 0, "incorrect": 0, "skipped": 0, "time": 0
            }
        
        subject_map[subj]["total"] += 1
        subject_map[subj]["time"] += time_s
        subject_map[subj]["topics"][topic]["total"] += 1
        subject_map[subj]["topics"][topic]["time"] += time_s
        
        if ans.selected_option_index is None:
            subject_map[subj]["skipped"] += 1
            subject_map[subj]["time_skipped"] += time_s
            subject_map[subj]["topics"][topic]["skipped"] += 1
        else:
            is_correct = False
            options = getattr(ans.question, "options", [])
            idx = ans.selected_option_index
            if options and isinstance(options, list) and 0 <= idx < len(options):
                is_correct = options[idx].get("is_correct", False)

            if is_correct:
                subject_map[subj]["correct"] += 1
                subject_map[subj]["time_correct"] += time_s
                subject_map[subj]["topics"][topic]["correct"] += 1
            else:
                subject_map[subj]["incorrect"] += 1
                subject_map[subj]["time_incorrect"] += time_s
                subject_map[subj]["topics"][topic]["incorrect"] += 1
    
    return subject_map


def _map_to_performances(subject_map) -> list:
    """Convert a subject_map dict into a list of SubjectPerformance objects."""
    performances = []
    for subj, stats in subject_map.items():
        acc = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        avg_time = (stats["time"] / stats["total"]) if stats["total"] > 0 else 0
        
        topic_perfs = []
        for topic_name, t_stats in stats.get("topics", {}).items():
            t_acc = (t_stats["correct"] / t_stats["total"] * 100) if t_stats["total"] > 0 else 0
            t_avg_time = (t_stats["time"] / t_stats["total"]) if t_stats["total"] > 0 else 0
            topic_perfs.append(TopicPerformance(
                topic=topic_name,
                total_questions=t_stats["total"],
                correct=t_stats["correct"],
                incorrect=t_stats["incorrect"],
                skipped=t_stats.get("skipped", 0),
                accuracy_percentage=round(t_acc, 2),
                avg_time_seconds=round(t_avg_time, 1)
            ))
        
        # Sort topics by accuracy (weakest first)
        topic_perfs.sort(key=lambda x: x.accuracy_percentage)
        
        performances.append(SubjectPerformance(
            subject=subj,
            total_questions=stats["total"],
            correct=stats["correct"],
            incorrect=stats["incorrect"],
            skipped=stats["skipped"],
            accuracy_percentage=round(acc, 2),
            time_spent_seconds=stats["time"],
            avg_time_seconds=round(avg_time, 1),
            time_on_correct=stats.get("time_correct", 0),
            time_on_incorrect=stats.get("time_incorrect", 0),
            time_on_skipped=stats.get("time_skipped", 0),
            topics=topic_perfs
        ))
    
    return performances


def _generate_insights(performances) -> list:
    """Generate smart insights from subject+topic performances, including time-based analysis."""
    insights = []
    
    if not performances:
        return ["Take a test to generate insights."]
    
    # Find weakest subject
    weakest = min(performances, key=lambda x: x.accuracy_percentage)
    strongest = max(performances, key=lambda x: x.accuracy_percentage)
    
    if weakest.accuracy_percentage < 60:
        insights.append(
            f"Focus Alert: Your accuracy in '{weakest.subject}' is lowest at {weakest.accuracy_percentage}%. "
            f"You skipped {weakest.skipped} questions in this topic. "
            f"We recommend reviewing your '{weakest.subject}' notes."
        )
        
        # Drill into weakest topics within the weakest subject
        if weakest.topics:
            worst_topic = weakest.topics[0]  # Already sorted by accuracy
            if worst_topic.accuracy_percentage < 50:
                insights.append(
                    f"🎯 Targeted Alert: Within '{weakest.subject}', your weakest area is "
                    f"'{worst_topic.topic}' at {worst_topic.accuracy_percentage}% accuracy "
                    f"({worst_topic.correct}/{worst_topic.total_questions} correct). "
                    f"Practice this specific topic to see the fastest improvement."
                )
    else:
        insights.append(
            "Great job! Your accuracy is consistently good across all subjects. "
            "Consider taking advanced mock tests."
        )
    
    if strongest.accuracy_percentage >= 80:
        insights.append(
            f"Strength: '{strongest.subject}' is your strongest subject with "
            f"{strongest.accuracy_percentage}% accuracy."
        )
    
    # ─── TIME-BASED INSIGHTS ───
    total_time_wasted = 0
    total_time_all = 0
    
    for perf in performances:
        total_time_all += perf.time_spent_seconds
        wasted = perf.time_on_incorrect + perf.time_on_skipped
        total_time_wasted += wasted
        
        # Slow but correct: avg > 90 seconds and accuracy >= 60%
        if perf.avg_time_seconds > 90 and perf.accuracy_percentage >= 60:
            insights.append(
                f"⏱️ Speed Alert: You're accurate in '{perf.subject}' ({perf.accuracy_percentage}%) "
                f"but averaging {perf.avg_time_seconds:.0f}s per question. "
                f"Find faster solving methods to save time for harder questions."
            )
        
        # Time on wrong answers
        if perf.time_on_incorrect > 0 and perf.incorrect > 0:
            avg_wrong_time = perf.time_on_incorrect / perf.incorrect
            if avg_wrong_time > 60:
                insights.append(
                    f"⚠️ Time Drain: You spent {perf.time_on_incorrect // 60}m {perf.time_on_incorrect % 60}s "
                    f"on {perf.incorrect} wrong answers in '{perf.subject}' "
                    f"(avg {avg_wrong_time:.0f}s each). Learn these concepts first — "
                    f"spending time without knowing the concept hurts doubly."
                )
        
        # Time on skipped questions
        if perf.time_on_skipped > 0 and perf.skipped > 0:
            avg_skip_time = perf.time_on_skipped / perf.skipped
            if avg_skip_time > 30:
                insights.append(
                    f"🚫 Wasted Time: You spent {perf.time_on_skipped // 60}m {perf.time_on_skipped % 60}s "
                    f"on {perf.skipped} questions you didn't even answer in '{perf.subject}' "
                    f"(avg {avg_skip_time:.0f}s each). If you don't know a concept, "
                    f"skip within 15 seconds — save time for questions you can solve!"
                )
    
    # Overall wasted time summary
    if total_time_wasted > 60:
        wasted_mins = total_time_wasted // 60
        wasted_pct = round((total_time_wasted / total_time_all * 100) if total_time_all > 0 else 0, 1)
        insights.append(
            f"📊 Time Audit: You spent {wasted_mins} minutes ({wasted_pct}% of your test time) "
            f"on questions you got wrong or left blank. Reducing this wasted time "
            f"can directly improve your score."
        )
    
    return insights


async def get_attempt_analytics(db: AsyncSession, attempt_id: uuid.UUID, user_id: uuid.UUID) -> AttemptAnalyticsResponse:
    stmt = (
        select(Attempt)
        .options(
            selectinload(Attempt.user_answers).selectinload(UserAnswer.question),
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
    
    subject_map = _build_performance_map(attempt.user_answers)
    performances = _map_to_performances(subject_map)
    
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
    
    # Aggregate all answers across attempts
    all_answers = []
    for attempt in attempts:
        all_answers.extend(attempt.user_answers)
    
    subject_map = _build_performance_map(all_answers)
    performances = _map_to_performances(subject_map)
        
    return SeriesAnalyticsResponse(
        course_id=str(course_id),
        total_attempts=len(attempts),
        average_score=round(avg_score, 2),
        subject_performances=performances
    )

from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.enrollment import Enrollment
from app.models.test_series import TestSeries
from app.models.result import Result
from app.models.section import Section
from app.models.question import Question
from sqlalchemy import func

async def get_analytics_hierarchy(db: AsyncSession, user_id: uuid.UUID) -> list:
    stmt = (
        select(Enrollment)
        .options(
            selectinload(Enrollment.course).selectinload(Course.subcategory).selectinload(SubCategory.category)
        )
        .where(Enrollment.user_id == user_id)
    )
    res = await db.execute(stmt)
    enrollments = res.scalars().all()
    
    cat_map = {}
    for e in enrollments:
        if not e.course:
            continue
        c_title = e.course.title
        c_id = str(e.course.id)
        
        cat_name = "General"
        if e.course.subcategory and e.course.subcategory.category:
            cat_name = e.course.subcategory.category.name
            
        if cat_name not in cat_map:
            cat_map[cat_name] = []
        cat_map[cat_name].append({"course_id": c_id, "title": c_title})
        
    hierarchy = []
    for c_name, courses in cat_map.items():
        hierarchy.append({
            "category_name": c_name,
            "courses": courses
        })
    return hierarchy

async def get_course_overall_analytics(db: AsyncSession, course_id: uuid.UUID, user_id: uuid.UUID):
    stmt = select(Course).options(selectinload(Course.folders).selectinload(CourseFolder.tests)).where(Course.id == course_id)
    res = await db.execute(stmt)
    course = res.scalars().first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
        
    test_ids = [t.test_id for f in course.folders for t in f.tests]
    
    available_tests = []
    if test_ids:
        tests_stmt = select(TestSeries).where(TestSeries.id.in_(test_ids))
        tests_res = await db.execute(tests_stmt)
        tests = tests_res.scalars().all()
        available_tests = [{"course_id": str(t.id), "title": t.title} for t in tests]
    
    if not test_ids:
        return {
            "course_id": str(course_id),
            "course_title": course.title,
            "overall_accuracy": 0.0,
            "course_percentile": 0.0,
            "total_attempts": 0,
            "subject_performances": [],
            "insights": ["Take a test to generate insights."],
            "available_tests": []
        }
        
    stmt = (
        select(Attempt)
        .options(
            selectinload(Attempt.user_answers).selectinload(UserAnswer.question),
            selectinload(Attempt.result)
        )
        .where(Attempt.user_id == user_id, Attempt.test_series_id.in_(test_ids), Attempt.status == AttemptStatus.SUBMITTED)
    )
    res = await db.execute(stmt)
    attempts = res.scalars().unique().all()
    
    total_attempts = len(attempts)
    if total_attempts == 0:
        return {
            "course_id": str(course_id),
            "course_title": course.title,
            "overall_accuracy": 0.0,
            "course_percentile": 0.0,
            "total_attempts": 0,
            "subject_performances": [],
            "insights": ["Take a test to generate insights."],
            "available_tests": available_tests
        }
        
    user_total_score = sum(a.result.total_score for a in attempts if a.result)
    
    user_scores_stmt = select(Attempt.user_id, func.sum(Result.total_score).label('total_sum')).join(Result).where(
        Attempt.test_series_id.in_(test_ids),
        Attempt.status == AttemptStatus.SUBMITTED
    ).group_by(Attempt.user_id)
    
    all_user_scores = (await db.execute(user_scores_stmt)).all()
    higher_scores = sum(1 for row in all_user_scores if row.total_sum > user_total_score)
    total_users = len(all_user_scores)
    
    if total_users > 1:
        percentile = ((total_users - (higher_scores + 1)) / total_users) * 100
    else:
        percentile = 100.0
    
    # Aggregate all answers
    all_answers = []
    for attempt in attempts:
        all_answers.extend(attempt.user_answers)
    
    subject_map = _build_performance_map(all_answers)
    performances = _map_to_performances(subject_map)
    
    total_correct = sum(p.correct for p in performances)
    total_q = sum(p.total_questions for p in performances)
    overall_accuracy = (total_correct / total_q * 100) if total_q > 0 else 0.0
    
    insights = _generate_insights(performances)
    
    return {
        "course_id": str(course_id),
        "course_title": course.title,
        "overall_accuracy": round(overall_accuracy, 2),
        "course_percentile": round(percentile, 2),
        "total_attempts": total_attempts,
        "subject_performances": performances,
        "insights": insights,
        "available_tests": available_tests
    }

async def get_specific_test_analytics(db: AsyncSession, test_series_id: uuid.UUID, user_id: uuid.UUID):
    stmt = (
        select(Attempt)
        .options(
            selectinload(Attempt.test_series),
            selectinload(Attempt.user_answers).selectinload(UserAnswer.question),
            selectinload(Attempt.result)
        )
        .where(Attempt.test_series_id == test_series_id, Attempt.user_id == user_id, Attempt.status == AttemptStatus.SUBMITTED)
        .order_by(Attempt.started_at.desc())
    )
    res = await db.execute(stmt)
    attempt = res.scalars().first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="No submitted attempt found for this test")
    
    subject_map = _build_performance_map(attempt.user_answers)
    performances = _map_to_performances(subject_map)
    
    result_obj = attempt.result
    rank = result_obj.rank if result_obj and result_obj.rank else 0
    percentile = result_obj.percentile if result_obj and result_obj.percentile else 0.0
    acc = result_obj.accuracy_percentage if result_obj else 0.0
    
    insights = _generate_insights(performances)
            
    return {
        "test_series_id": str(test_series_id),
        "test_title": attempt.test_series.title if attempt.test_series else "Test",
        "total_score": result_obj.total_score if result_obj else 0.0,
        "rank": rank,
        "percentile": percentile,
        "accuracy": round(acc, 2),
        "subject_performances": performances,
        "insights": insights
    }


# --- POST-TEST RESULTS PAGE (The X-Factor) ---

async def get_post_test_results(db: AsyncSession, attempt_id: uuid.UUID, user_id: uuid.UUID) -> dict:
    """
    Comprehensive post-test results with:
    - Score, rank, percentile
    - Subject + topic breakdown
    - Weak/strong topic identification
    - Psychological nudges (loss aversion, social proof, progress anchoring)
    """
    stmt = (
        select(Attempt)
        .options(
            selectinload(Attempt.test_series).selectinload(TestSeries.sections).selectinload(Section.questions),
            selectinload(Attempt.user_answers).selectinload(UserAnswer.question),
            selectinload(Attempt.result)
        )
        .where(Attempt.id == attempt_id, Attempt.user_id == user_id)
    )
    res = await db.execute(stmt)
    attempt = res.scalars().first()
    
    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")
    if attempt.status != AttemptStatus.SUBMITTED:
        raise HTTPException(status_code=400, detail="Attempt is not submitted yet")
    
    result_obj = attempt.result
    test_series = attempt.test_series
    
    # Build performances
    subject_map = _build_performance_map(attempt.user_answers)
    performances = _map_to_performances(subject_map)
    
    # Identify weak and strong topics
    weak_topics = []
    strong_topics = []
    
    for perf in performances:
        for tp in perf.topics:
            topic_info = {
                "subject": perf.subject,
                "topic": tp.topic,
                "accuracy": tp.accuracy_percentage,
                "total_attempted": tp.total_questions,
                "practice_question_count": 0  # Will be filled by frontend if needed
            }
            if tp.accuracy_percentage < 60:
                weak_topics.append(topic_info)
            elif tp.accuracy_percentage >= 75:
                strong_topics.append(topic_info)
    
    # Sort by accuracy
    weak_topics.sort(key=lambda x: x["accuracy"])
    strong_topics.sort(key=lambda x: -x["accuracy"])
    
    # Calculate total questions in test
    total_qs_in_test = 0
    if test_series and test_series.sections:
        for s in test_series.sections:
            total_qs_in_test += len(s.questions) if s.questions else 0
    
    # Generate psychological nudges
    nudges = []
    
    # 1. Loss Aversion: Negative marking impact
    if result_obj:
        neg_mark = test_series.negative_marking if test_series else 0.25
        marks_lost = result_obj.incorrect_count * neg_mark
        if marks_lost > 0:
            hypothetical_score = result_obj.total_score + marks_lost
            nudges.append({
                "type": "loss_aversion",
                "message": f"You lost {marks_lost:.1f} marks to negative marking. "
                           f"Even {min(5, result_obj.incorrect_count)} fewer wrong answers would have given you "
                           f"{result_obj.total_score + min(5, result_obj.incorrect_count) * (neg_mark + 1):.1f} marks!",
                "icon": "⚠️"
            })
    
    # 2. Social Proof: Compare with top performers
    if result_obj and test_series:
        top_results = (await db.execute(
            select(Result.total_score)
            .join(Attempt)
            .where(
                Attempt.test_series_id == test_series.id,
                Attempt.status == AttemptStatus.SUBMITTED
            )
            .order_by(Result.total_score.desc())
            .limit(max(1, int(len(await _get_all_attempts_count(db, test_series.id)) * 0.1)))
        )).scalars().all()
        
        if top_results:
            top_avg = sum(top_results) / len(top_results)
            if result_obj.total_score < top_avg:
                nudges.append({
                    "type": "social_proof",
                    "message": f"Top scorers averaged {top_avg:.1f} marks in this test. "
                               f"You're {top_avg - result_obj.total_score:.1f} marks away from the top tier!",
                    "icon": "👥"
                })
    
    # 3. Progress Anchoring: Distance from cut-off
    if result_obj:
        # Estimate cut-off as 60% of total possible marks
        total_possible = total_qs_in_test * (test_series.sections[0].marks_per_question if test_series and test_series.sections else 1.0)
        estimated_cutoff = total_possible * 0.6
        gap = estimated_cutoff - result_obj.total_score
        if gap > 0:
            nudges.append({
                "type": "progress_anchor",
                "message": f"You're just {gap:.1f} marks away from the estimated cut-off of {estimated_cutoff:.0f}. "
                           f"Practice your weak topics to close this gap!",
                "icon": "📊"
            })
        else:
            nudges.append({
                "type": "progress_anchor",
                "message": f"🎉 You've cleared the estimated cut-off by {abs(gap):.1f} marks! "
                           f"Keep sharpening your skills to maintain this lead.",
                "icon": "🏆"
            })
    
    # 4. Specificity Bias: Exact weak topic call-out
    if weak_topics:
        worst = weak_topics[0]
        nudges.append({
            "type": "specificity_bias",
            "message": f"You got only {int(worst['accuracy'])}% in '{worst['topic']}' under '{worst['subject']}'. "
                       f"Practice targeted questions to fix this specific weakness.",
            "icon": "🎯"
        })
    
    # Encouragement
    accuracy = result_obj.accuracy_percentage if result_obj else 0.0
    if accuracy >= 80:
        encouragement = "🏆 Outstanding performance! You're well-prepared for the exam!"
    elif accuracy >= 60:
        encouragement = "💪 Good effort! Focus on your weak areas and you'll ace it!"
    elif accuracy >= 40:
        encouragement = "📚 Keep going! Consistent practice will significantly boost your score."
    else:
        encouragement = "🎯 Every expert was once a beginner. Review the explanations and practice daily!"
    
    return {
        "attempt_id": str(attempt.id),
        "test_title": test_series.title if test_series else "Test",
        "total_score": result_obj.total_score if result_obj else 0.0,
        "rank": result_obj.rank if result_obj and result_obj.rank else 0,
        "percentile": result_obj.percentile if result_obj and result_obj.percentile else 0.0,
        "accuracy": round(accuracy, 2),
        "correct_count": result_obj.correct_count if result_obj else 0,
        "incorrect_count": result_obj.incorrect_count if result_obj else 0,
        "skipped_count": result_obj.skipped_count if result_obj else 0,
        "subject_performances": performances,
        "weak_topics": weak_topics,
        "strong_topics": strong_topics,
        "nudges": nudges,
        "encouragement": encouragement
    }


async def _get_all_attempts_count(db, test_series_id):
    """Helper to count total attempts for a test series."""
    stmt = select(Attempt.id).where(
        Attempt.test_series_id == test_series_id,
        Attempt.status == AttemptStatus.SUBMITTED
    )
    result = await db.execute(stmt)
    return result.scalars().all()
