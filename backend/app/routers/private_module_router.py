"""Private-module router — isolated quiz universes gated by email whitelist.

Two halves:
  * user-facing: list accessible modules, browse subjects/topics, take the quiz.
  * admin-facing: whitelist management (add/remove emails per module).
"""
import uuid
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User
from app.services import private_module_service as svc


router = APIRouter()


# ─────────── user-facing endpoints ───────────

@router.get("/modules")
async def list_my_modules(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """Modules this user's email is whitelisted for."""
    modules = await svc.list_accessible_modules(db, user.email)
    return {
        "modules": [
            {"slug": m.slug, "name": m.name, "description": m.description}
            for m in modules
        ]
    }


@router.get("/modules/{slug}")
async def get_module_home(
    slug: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    module = await svc.require_module_access(db, user.email, slug)
    subjects = await svc.module_subject_summary(db, module.id, user.id)
    return {
        "slug": module.slug,
        "name": module.name,
        "description": module.description,
        "subjects": subjects,
    }


@router.get("/modules/{slug}/subjects/{subject}/topics")
async def get_module_topics(
    slug: str,
    subject: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    module = await svc.require_module_access(db, user.email, slug)
    topics = await svc.module_topic_summary(db, module.id, subject)
    return {"subject": subject, "topics": topics}


@router.get("/modules/{slug}/quiz/{subject}")
async def get_module_quiz(
    slug: str,
    subject: str,
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    module = await svc.require_module_access(db, user.email, slug)
    questions = await svc.get_daily_quiz(db, module.id, user.id, subject, limit)
    return {"subject": subject, "questions": questions, "count": len(questions)}


@router.get("/modules/{slug}/weak-topics")
async def get_module_weak_topic_quiz(
    slug: str,
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    """Module-scoped suggestions. Never blends with non-module weak topics."""
    module = await svc.require_module_access(db, user.email, slug)
    return await svc.get_weak_topic_quiz(db, module.id, user.id, limit)


@router.post("/modules/{slug}/more-practice")
async def get_module_more_practice(
    slug: str,
    subject: str = Query(...),
    topic: Optional[str] = Query(None),
    exclude_ids: str = Query(""),
    limit: int = Query(10, ge=1, le=30),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    module = await svc.require_module_access(db, user.email, slug)
    excluded = [eid.strip() for eid in exclude_ids.split(",") if eid.strip()]
    qs = await svc.get_more_practice(db, module.id, user.id, subject, topic, excluded, limit)
    return {"subject": subject, "topic": topic, "questions": qs, "count": len(qs)}


class ModuleQuizAnswer(BaseModel):
    question_id: str
    selected_option_index: Optional[int] = None


class ModuleQuizSubmission(BaseModel):
    answers: List[ModuleQuizAnswer]


@router.post("/modules/{slug}/submit")
async def submit_module_quiz(
    slug: str,
    submission: ModuleQuizSubmission,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Any:
    module = await svc.require_module_access(db, user.email, slug)
    return await svc.submit_answers(
        db, module.id, user.id, [a.model_dump() for a in submission.answers]
    )


# ─────────── admin endpoints ───────────

@router.get("/admin/modules")
async def admin_list_modules(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    return {"modules": await svc.list_all_modules(db)}


@router.get("/admin/modules/{slug}/access")
async def admin_list_access(
    slug: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    module = await svc.get_module_by_slug(db, slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return {
        "slug": module.slug,
        "name": module.name,
        "access": await svc.list_access(db, module.id),
    }


class GrantAccessIn(BaseModel):
    email: str
    note: Optional[str] = None


@router.post("/admin/modules/{slug}/access")
async def admin_grant_access(
    slug: str,
    data: GrantAccessIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    module = await svc.get_module_by_slug(db, slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return await svc.grant_access(db, module.id, data.email, data.note, admin.id)


@router.delete("/admin/modules/{slug}/access/{access_id}")
async def admin_revoke_access(
    slug: str,
    access_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    module = await svc.get_module_by_slug(db, slug)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    return await svc.revoke_access(db, module.id, access_id)
