"""Flagged questions router — save/unsave questions for later review.

Users can flag any question during quiz/mock analysis and later review them
in a dedicated 'Saved Questions' section. Flags can be removed once mastered.

Supported sources:
  'quiz'           — questions from the main quiz_questions pool
  'private_module' — questions from private module banks (EPFO, AAO, etc.)
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, delete as sql_delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.flagged_question import UserFlaggedQuestion
from app.models.question import Question
from app.models.private_module import PrivateModuleQuestion
from app.models.user import User

router = APIRouter()

VALID_SOURCES = {"quiz", "private_module"}


class FlagRequest(BaseModel):
    question_source: str   # 'quiz' | 'private_module'
    question_id: str       # UUID string
    user_note: Optional[str] = None


class FlaggedOut(BaseModel):
    id: str
    question_source: str
    question_id: str
    user_note: Optional[str]
    flagged_at: str

    # question detail fields (populated on list)
    question_text: Optional[str] = None
    options: Optional[list] = None
    explanation: Optional[str] = None
    topic: Optional[str] = None
    subject: Optional[str] = None
    section: Optional[str] = None     # milestone section for AAO-type modules
    difficulty: Optional[str] = None


@router.post("/flag")
async def flag_question(
    body: FlagRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """Flag (save) a question for later review. Idempotent."""
    if body.question_source not in VALID_SOURCES:
        raise HTTPException(status_code=400,
                            detail=f"question_source must be one of {VALID_SOURCES}")

    existing = (await db.execute(
        select(UserFlaggedQuestion).where(
            UserFlaggedQuestion.user_id == user.id,
            UserFlaggedQuestion.question_source == body.question_source,
            UserFlaggedQuestion.question_id == body.question_id,
        )
    )).scalars().first()

    if existing:
        if body.user_note is not None:
            existing.user_note = body.user_note
            await db.commit()
        return {"status": "already_flagged", "id": str(existing.id)}

    flag = UserFlaggedQuestion(
        user_id=user.id,
        question_source=body.question_source,
        question_id=body.question_id,
        user_note=body.user_note,
    )
    db.add(flag)
    await db.commit()
    await db.refresh(flag)
    return {"status": "flagged", "id": str(flag.id)}


@router.delete("/flag")
async def unflag_question(
    question_source: str = Query(...),
    question_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """Remove a flag from a question."""
    result = await db.execute(
        sql_delete(UserFlaggedQuestion).where(
            UserFlaggedQuestion.user_id == user.id,
            UserFlaggedQuestion.question_source == question_source,
            UserFlaggedQuestion.question_id == question_id,
        )
    )
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Flag not found")
    return {"status": "unflagged"}


@router.get("/flagged")
async def list_flagged_questions(
    source: Optional[str] = Query(None, description="Filter by source: 'quiz' or 'private_module'"),
    limit: int = Query(100, le=500),
    offset: int = Query(0),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """List all flagged questions with full question details."""
    stmt = select(UserFlaggedQuestion).where(
        UserFlaggedQuestion.user_id == user.id
    )
    if source and source in VALID_SOURCES:
        stmt = stmt.where(UserFlaggedQuestion.question_source == source)
    stmt = stmt.order_by(UserFlaggedQuestion.flagged_at.desc()).offset(offset).limit(limit)
    flags = (await db.execute(stmt)).scalars().all()

    # Separate IDs by source
    quiz_ids = [f.question_id for f in flags if f.question_source == "quiz"]
    pm_ids = [f.question_id for f in flags if f.question_source == "private_module"]

    # Bulk-load question details
    quiz_map: dict = {}
    pm_map: dict = {}

    if quiz_ids:
        rows = (await db.execute(
            select(Question).where(Question.id.in_(quiz_ids))
        )).scalars().all()
        quiz_map = {str(q.id): q for q in rows}

    if pm_ids:
        rows = (await db.execute(
            select(PrivateModuleQuestion).where(
                PrivateModuleQuestion.id.in_(pm_ids)
            )
        )).scalars().all()
        pm_map = {str(q.id): q for q in rows}

    results = []
    for flag in flags:
        qid = flag.question_id
        detail: Any = None
        if flag.question_source == "quiz":
            detail = quiz_map.get(qid)
        else:
            detail = pm_map.get(qid)

        item: dict = {
            "id": str(flag.id),
            "question_source": flag.question_source,
            "question_id": qid,
            "user_note": flag.user_note,
            "flagged_at": flag.flagged_at.isoformat() if flag.flagged_at else None,
        }
        if detail:
            item["question_text"] = getattr(detail, "question_text", getattr(detail, "stem", ""))
            item["options"] = detail.options
            item["explanation"] = detail.explanation
            item["topic"] = detail.topic
            item["subject"] = detail.subject
            item["difficulty"] = getattr(detail, "difficulty", None)
            item["section"] = getattr(detail, "section", None)
        results.append(item)

    return {"total": len(results), "items": results}


@router.get("/flag/status")
async def check_flag_status(
    question_source: str = Query(...),
    question_id: str = Query(...),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """Check whether a specific question is flagged by the current user."""
    flag = (await db.execute(
        select(UserFlaggedQuestion).where(
            UserFlaggedQuestion.user_id == user.id,
            UserFlaggedQuestion.question_source == question_source,
            UserFlaggedQuestion.question_id == question_id,
        )
    )).scalars().first()
    return {"is_flagged": flag is not None, "flag_id": str(flag.id) if flag else None}
