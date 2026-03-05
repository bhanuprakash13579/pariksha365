"""
Quiz Router — Endpoints for the adaptive quiz system.
Daily quizzes by category, weak-topic recommended quizzes, and exhaustive practice.
"""
from typing import Any, List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.services import practice_service, gemini_service, pdf_scraper_service
from pydantic import BaseModel

router = APIRouter()


class QuizAnswerSubmit(BaseModel):
    question_id: str
    selected_option_index: Optional[int] = None


class QuizSubmission(BaseModel):
    answers: List[QuizAnswerSubmit]


# --- Public Quiz Endpoints ---

@router.get("/categories")
async def get_quiz_categories(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Any:
    """Get all quiz categories with question counts."""
    categories = await practice_service.get_quiz_categories_with_counts(db)
    streak = await practice_service.get_streak_info(db, user.id)
    return {
        "categories": categories,
        "streak": streak
    }


@router.get("/daily/{subject}")
async def get_daily_quiz(
    subject: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=30)
) -> Any:
    """Get a daily quiz for a specific subject category."""
    questions = await practice_service.get_daily_quiz(db, user.id, subject, limit)
    return {
        "subject": subject,
        "questions": questions,
        "count": len(questions)
    }


@router.get("/weak-topics")
async def get_weak_topic_quiz(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=30)
) -> Any:
    """Get a personalized quiz based on user's weakest topics. The RECOMMENDED quiz."""
    return await practice_service.get_weak_topic_quiz(db, user.id, limit)


@router.post("/more-practice")
async def get_more_practice(
    subject: str = Query(...),
    topic: Optional[str] = Query(None),
    exclude_ids: str = Query(""),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=30)
) -> Any:
    """Get more practice questions (exhaustive practice flow)."""
    excluded = [eid.strip() for eid in exclude_ids.split(",") if eid.strip()]
    return await practice_service.get_more_practice(db, user.id, subject, topic, excluded, limit)


@router.post("/submit")
async def submit_quiz(
    submission: QuizSubmission,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Any:
    """Submit quiz answers and get scorecard."""
    answers = [a.model_dump() for a in submission.answers]
    return await practice_service.submit_quiz_answers(db, user.id, answers)


@router.get("/streak")
async def get_streak(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Any:
    """Get user's streak information."""
    return await practice_service.get_streak_info(db, user.id)


@router.get("/weak-topics/list")
async def get_user_weak_topics(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
) -> Any:
    """Get the user's current weak topics (for display on analytics page)."""
    from app.models.quiz_pool import UserWeakTopic
    from sqlalchemy.future import select
    
    stmt = (
        select(UserWeakTopic)
        .where(UserWeakTopic.user_id == user.id)
        .order_by(UserWeakTopic.accuracy.asc())
    )
    topics = (await db.execute(stmt)).scalars().all()
    
    return {
        "weak_topics": [
            {
                "subject": t.subject,
                "topic": t.topic,
                "accuracy": round(t.accuracy, 1),
                "total_questions": t.total_questions,
                "correct_count": t.correct_count,
                "is_critical": t.accuracy < 40
            }
            for t in topics if t.accuracy < 60
        ],
        "strong_topics": [
            {
                "subject": t.subject,
                "topic": t.topic,
                "accuracy": round(t.accuracy, 1),
                "total_questions": t.total_questions
            }
            for t in topics if t.accuracy >= 60
        ]
    }


# --- Admin Quiz Endpoints ---

@router.post("/admin/upload-pdf")
async def upload_quiz_pdf(
    file: UploadFile = File(...),
    ai_classify: bool = Query(True, description="Use Gemini AI to auto-classify questions"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Upload a PDF of quiz questions. Extracts, classifies, and adds to quiz pool.
    Uses Gemini AI for auto-classification when ai_classify=true.
    """
    # Step 1: Extract raw questions from PDF
    raw_questions = await pdf_scraper_service.extract_text_and_images(file)
    
    if not raw_questions:
        return {"status": "error", "message": "No questions could be extracted from the PDF."}
    
    # Step 2: Classify with Gemini (if enabled)
    if ai_classify:
        classified = await gemini_service.classify_questions(raw_questions)
    else:
        classified = raw_questions
    
    # Step 3: Insert into quiz pool
    result = await practice_service.upload_quiz_questions(db, classified)
    
    return {
        "status": "success",
        "extracted": len(raw_questions),
        **result
    }


@router.post("/admin/upload-json")
async def upload_quiz_json(
    questions: List[dict],
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Manually upload pre-classified quiz questions as JSON."""
    return await practice_service.upload_quiz_questions(db, questions)


# --- Admin Quiz CRUD Endpoints ---


class QuizQuestionCreate(BaseModel):
    question_text: str
    options: List[dict]
    subject: str
    topic: Optional[str] = "General"
    topic_code: Optional[str] = None
    explanation: Optional[str] = ""
    difficulty: Optional[str] = "MEDIUM"
    image_url: Optional[str] = None


class QuizQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    options: Optional[List[dict]] = None
    subject: Optional[str] = None
    topic: Optional[str] = None
    topic_code: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None
    image_url: Optional[str] = None


@router.get("/admin/questions")
async def list_quiz_questions(
    subject: Optional[str] = Query(None),
    topic: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """List all quiz pool questions with filtering and pagination."""
    from app.models.quiz_pool import QuizQuestion
    from sqlalchemy.future import select
    from sqlalchemy import func as sqlfunc

    conditions = []
    if subject:
        conditions.append(sqlfunc.lower(QuizQuestion.subject) == subject.lower())
    if topic:
        conditions.append(sqlfunc.lower(QuizQuestion.topic) == topic.lower())
    if search:
        conditions.append(QuizQuestion.question_text.ilike(f"%{search}%"))

    # Count total
    count_stmt = select(sqlfunc.count(QuizQuestion.id))
    if conditions:
        count_stmt = count_stmt.where(*conditions)
    total = (await db.execute(count_stmt)).scalar() or 0

    # Fetch page
    stmt = select(QuizQuestion).order_by(QuizQuestion.created_at.desc())
    if conditions:
        stmt = stmt.where(*conditions)
    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    questions = (await db.execute(stmt)).scalars().all()

    # Get unique subjects and topics for filters
    subjects_stmt = select(QuizQuestion.subject).distinct()
    subjects = [r[0] for r in (await db.execute(subjects_stmt)).all() if r[0]]
    topics_stmt = select(QuizQuestion.topic).distinct()
    topics = [r[0] for r in (await db.execute(topics_stmt)).all() if r[0]]

    return {
        "questions": [practice_service._serialize_quiz_question(q) for q in questions],
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "filters": {"subjects": sorted(subjects), "topics": sorted(topics)},
    }


@router.post("/admin/questions")
async def create_quiz_question(
    data: QuizQuestionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Create a single quiz question in the pool."""
    from app.models.quiz_pool import QuizQuestion

    q = QuizQuestion(
        question_text=data.question_text,
        options=[{"option_text": o.get("option_text", ""), "is_correct": o.get("is_correct", False)} for o in data.options],
        subject=data.subject,
        topic=data.topic or "General",
        topic_code=data.topic_code,
        explanation=data.explanation or "",
        difficulty=data.difficulty or "MEDIUM",
        image_url=data.image_url,
    )
    db.add(q)
    await db.commit()
    await db.refresh(q)
    return practice_service._serialize_quiz_question(q)


@router.put("/admin/questions/{question_id}")
async def update_quiz_question(
    question_id: uuid.UUID,
    data: QuizQuestionUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Update a quiz question in the pool."""
    from app.models.quiz_pool import QuizQuestion
    from sqlalchemy.future import select
    from fastapi import HTTPException

    q = (await db.execute(select(QuizQuestion).where(QuizQuestion.id == question_id))).scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    if data.question_text is not None: q.question_text = data.question_text
    if data.options is not None: q.options = [{"option_text": o.get("option_text", ""), "is_correct": o.get("is_correct", False)} for o in data.options]
    if data.subject is not None: q.subject = data.subject
    if data.topic is not None: q.topic = data.topic
    if data.topic_code is not None: q.topic_code = data.topic_code
    if data.explanation is not None: q.explanation = data.explanation
    if data.difficulty is not None: q.difficulty = data.difficulty
    if data.image_url is not None: q.image_url = data.image_url

    db.add(q)
    await db.commit()
    await db.refresh(q)
    return practice_service._serialize_quiz_question(q)


@router.delete("/admin/questions/{question_id}")
async def delete_quiz_question(
    question_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Delete a quiz question from the pool."""
    from app.models.quiz_pool import QuizQuestion
    from sqlalchemy.future import select
    from fastapi import HTTPException

    q = (await db.execute(select(QuizQuestion).where(QuizQuestion.id == question_id))).scalars().first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    await db.delete(q)
    await db.commit()
    return {"status": "deleted", "id": str(question_id)}


# --- Bulk Upload ---


class BulkUploadRequest(BaseModel):
    questions: List[dict]


@router.post("/admin/bulk-upload")
async def bulk_upload_quiz_questions(
    payload: BulkUploadRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Bulk upload quiz questions with auto-normalization.
    Accepts a JSON array of questions, normalizes tags, and inserts into the pool.
    """
    if not payload.questions:
        return {"status": "error", "message": "No questions provided."}

    result = await practice_service.upload_quiz_questions(db, payload.questions)
    return {"status": "success", **result}


# --- Taxonomy Management ---


from app.services import taxonomy_service


@router.get("/admin/taxonomy")
async def get_taxonomy(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Get the full taxonomy tree."""
    return await taxonomy_service.get_all(db)


class TaxonomyEntryCreate(BaseModel):
    subject: str
    topic: str
    topic_code: str
    aliases: Optional[List[str]] = []


class TaxonomyEntryUpdate(BaseModel):
    subject: Optional[str] = None
    topic: Optional[str] = None
    topic_code: Optional[str] = None
    aliases: Optional[List[str]] = None


@router.get("/admin/taxonomy/codes")
async def get_all_topic_codes(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Get flat list of all topic codes for dropdown."""
    return await taxonomy_service.get_all_codes_flat(db)


@router.post("/admin/taxonomy")
async def create_taxonomy_entry(
    data: TaxonomyEntryCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Add a new subject→topic entry to the taxonomy."""
    try:
        entry = await taxonomy_service.create_entry(db, data.subject, data.topic, data.topic_code, data.aliases or [])
        return {"status": "created", "id": str(entry.id), "subject": entry.subject, "topic": entry.topic, "topic_code": entry.topic_code}
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/admin/taxonomy/{entry_id}")
async def update_taxonomy_entry(
    entry_id: uuid.UUID,
    data: TaxonomyEntryUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Update a taxonomy entry."""
    try:
        entry = await taxonomy_service.update_entry(db, entry_id, data.subject, data.topic, data.topic_code, data.aliases)
        return {"status": "updated", "id": str(entry.id), "subject": entry.subject, "topic": entry.topic, "topic_code": entry.topic_code}
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/admin/taxonomy/{entry_id}")
async def delete_taxonomy_entry(
    entry_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Delete a taxonomy entry."""
    try:
        await taxonomy_service.delete_entry(db, entry_id)
        return {"status": "deleted", "id": str(entry_id)}
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/admin/taxonomy/seed")
async def seed_taxonomy(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """Seed the default taxonomy (only if table is empty)."""
    return await taxonomy_service.seed_default_taxonomy(db)
