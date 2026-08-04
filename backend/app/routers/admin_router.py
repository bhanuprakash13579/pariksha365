from typing import Any, List, Optional
from fastapi import APIRouter, Depends, UploadFile, File, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.test_schema import TestSeriesCreate, TestSeriesResponse, SectionCreate, SectionResponse
from app.schemas.question_schema import QuestionCreate, QuestionResponse
from app.services import test_series_service, pdf_scraper_service, gemini_service, admin_analytics_service
from pydantic import BaseModel

router = APIRouter()

@router.get("/analytics/overview")
async def get_admin_analytics(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Returns platform-wide admin analytics in a single cached call.
    Results are cached for 5 minutes — zero performance overhead.
    """
    return await admin_analytics_service.get_overview(db)

@router.get("/test-series/coverage")
async def admin_test_series_coverage(
    test_type: str = Query(None, description="Filter by 'PYQ' or 'MOCK'. Omit for both."),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    """Per-paper coverage report for the admin panel.

    For every TestSeries returns the actual loaded question count vs the
    sanctioned count from the linked ExamPattern, plus the current
    is_published state and a stable test_id so the admin UI can render a
    publish-toggle next to each row.

    Use this to decide which gated papers to publish manually (e.g. paper
    that's 99/100 but the missing Q is non-critical) or which currently-
    published papers to pull (e.g. an outlier with a wrong answer key
    flagged by users).
    """
    from sqlalchemy import select, func
    from sqlalchemy.orm import selectinload
    from app.models.test_series import TestSeries
    from app.models.section import Section
    from app.models.question import Question
    from app.models.exam_stage import ExamStage
    from app.models.exam_pattern import ExamPattern
    from app.models.subcategory import SubCategory
    from app.models.category import Category

    stmt = (
        select(TestSeries)
        .options(
            selectinload(TestSeries.exam_stage)
            .selectinload(ExamStage.exam_pattern),
            selectinload(TestSeries.exam_stage)
            .selectinload(ExamStage.subcategory)
            .selectinload(SubCategory.category),
        )
        .order_by(TestSeries.title)
    )
    if test_type:
        stmt = stmt.where(TestSeries.test_type == test_type.upper())
    test_series = (await db.execute(stmt)).scalars().all()

    # Fetch actual counts in one round-trip — never N+1 even with hundreds of papers.
    counts_stmt = (
        select(Section.test_series_id, func.count(Question.id))
        .join(Question, Question.section_id == Section.id)
        .group_by(Section.test_series_id)
    )
    counts = {row[0]: row[1] for row in (await db.execute(counts_stmt)).all()}

    out = []
    for ts in test_series:
        stage = ts.exam_stage
        pattern = stage.exam_pattern if stage else None
        sanctioned = pattern.total_questions if pattern else None
        actual = counts.get(ts.id, 0)

        # Coverage percentage and a status flag for UI badging.
        if sanctioned and sanctioned > 0:
            coverage_pct = round(actual / sanctioned * 100, 1)
        else:
            coverage_pct = None
        if sanctioned is None:
            status = "no_pattern"
        elif actual == sanctioned:
            status = "complete"
        elif actual >= sanctioned * 0.95:
            status = "near_complete"
        elif actual >= sanctioned * 0.5:
            status = "partial"
        else:
            status = "fragment"

        sub = stage.subcategory if stage else None
        cat = sub.category if sub else None
        out.append({
            "id": str(ts.id),
            "title": ts.title,
            "test_type": ts.test_type.value if hasattr(ts.test_type, "value") else ts.test_type,
            "actual": actual,
            "sanctioned": sanctioned,
            "coverage_pct": coverage_pct,
            "status": status,
            "is_published": ts.is_published,
            "category": cat.name if cat else None,
            "subcategory": sub.name if sub else None,
            "stage": stage.name if stage else None,
            "stage_id": str(stage.id) if stage else None,
            "total_duration_minutes": ts.total_duration_minutes,
            "has_sectional_timing": bool(ts.has_sectional_timing),
            "negative_marking": ts.negative_marking,
            "paper_date": ts.paper_date.isoformat() if ts.paper_date else None,
        })

    # Aggregate stats for the header strip in the admin UI.
    summary = {
        "total": len(out),
        "published": sum(1 for r in out if r["is_published"]),
        "complete": sum(1 for r in out if r["status"] == "complete"),
        "near_complete": sum(1 for r in out if r["status"] == "near_complete"),
        "partial": sum(1 for r in out if r["status"] == "partial"),
        "fragment": sum(1 for r in out if r["status"] == "fragment"),
        "no_pattern": sum(1 for r in out if r["status"] == "no_pattern"),
    }
    return {"summary": summary, "papers": out}


class PublishToggleIn(BaseModel):
    is_published: bool


class TestSeriesMetaPatch(BaseModel):
    """Light-weight metadata patch — only fields safe to change without
    touching the section/question tree (which is content, not metadata).
    All fields optional; unset fields stay as-is."""
    title: Optional[str] = None
    description: Optional[str] = None
    paper_date: Optional[str] = None  # ISO date "YYYY-MM-DD"
    paper_shift: Optional[str] = None


@router.patch("/test-series/{test_id}")
async def admin_update_test_series_meta(
    test_id: uuid.UUID,
    payload: TestSeriesMetaPatch,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    """Rename / re-describe a TestSeries without touching its questions.

    Required because the existing PUT /tests/{test_id} on test_series_router
    is a FULL replace (expects every section + question in the payload), so
    it can't be used to edit just the title from the admin UI. This PATCH
    accepts a partial body — title alone, description alone, etc.
    """
    from sqlalchemy import select
    from app.models.test_series import TestSeries
    from fastapi import HTTPException
    from datetime import date as _date

    ts = (await db.execute(
        select(TestSeries).where(TestSeries.id == test_id)
    )).scalar_one_or_none()
    if ts is None:
        raise HTTPException(status_code=404, detail="Test series not found")
    if payload.title is not None:
        new_title = payload.title.strip()
        if not new_title:
            raise HTTPException(status_code=400, detail="Title must not be empty")
        ts.title = new_title
    if payload.description is not None:
        ts.description = payload.description
    if payload.paper_date is not None:
        try:
            ts.paper_date = _date.fromisoformat(payload.paper_date) if payload.paper_date else None
        except ValueError:
            raise HTTPException(status_code=400, detail="paper_date must be YYYY-MM-DD")
    if payload.paper_shift is not None:
        ts.paper_shift = payload.paper_shift or None
    await db.commit()
    return {
        "id": str(ts.id),
        "title": ts.title,
        "description": ts.description,
        "paper_date": ts.paper_date.isoformat() if ts.paper_date else None,
        "paper_shift": ts.paper_shift,
    }


@router.put("/test-series/{test_id}/publish-toggle")
async def admin_toggle_test_series_publish(
    test_id: uuid.UUID,
    payload: PublishToggleIn,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    """Manually flip a TestSeries's is_published flag from the admin panel.

    The loader's 100% gate is the default policy; this endpoint is the
    override an admin uses when they want to publish a slightly-incomplete
    paper (e.g. a 98/100 with the missing Qs being trivially low-stakes)
    or unpublish a paper students complain about.
    """
    from sqlalchemy import select
    from app.models.test_series import TestSeries
    from fastapi import HTTPException

    ts = (await db.execute(
        select(TestSeries).where(TestSeries.id == test_id)
    )).scalar_one_or_none()
    if ts is None:
        raise HTTPException(status_code=404, detail="Test series not found")
    ts.is_published = bool(payload.is_published)
    await db.commit()
    return {"id": str(ts.id), "is_published": ts.is_published}


@router.post("/test-series", response_model=TestSeriesResponse)
async def create_test(
    test_in: TestSeriesCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.create_test_series(db, test_in)

@router.post("/test-series/{test_id}/sections", response_model=SectionResponse)
async def add_section(
    test_id: uuid.UUID,
    section_in: SectionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.create_section(db, test_id, section_in)

@router.post("/sections/{section_id}/questions", response_model=QuestionResponse)
async def add_question(
    section_id: uuid.UUID,
    question_in: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    return await test_series_service.create_question(db, section_id, question_in)

from pydantic import BaseModel

class RawTextScrapeRequest(BaseModel):
    raw_text: str
    ai_classify: bool = False

@router.post("/questions/scrape-pdf")
async def scrape_pdf(
    file: UploadFile = File(...),
    ai_classify: bool = Query(False, description="Use AI to auto-classify questions with subject, topic, difficulty"),
    ai_model: str = Query("tesseract", description="AI Model: 'gemini', 'chatgpt', 'tesseract', or 'pymupdf'"),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Extracts text and images from a PDF using specified AI or OCR engine.
    """
    questions = await pdf_scraper_service.extract_text_and_images(file, ai_model=ai_model)
    
    if ai_classify and questions:
        questions = await gemini_service.classify_questions(questions)
    
    return {"status": "success", "ai_model": ai_model, "ai_classified": ai_classify, "data": questions}

@router.post("/questions/scrape-text")
async def scrape_text(
    request: RawTextScrapeRequest,
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Extracts questions from a raw pasted text block or HTML using Regex extraction.
    """
    questions = await pdf_scraper_service.extract_from_raw_text(request.raw_text)
    
    if request.ai_classify and questions:
        questions = await gemini_service.classify_questions(questions)
        
    return {"status": "success", "ai_classified": request.ai_classify, "data": questions}

import os
import cloudinary
import cloudinary.uploader
from fastapi import HTTPException
from app.models.notes import Note
from app.services.r2_storage_service import r2_storage

# Ensure Cloudinary is configured (either via CLOUDINARY_URL env var or manually)
# cloudinary.config(cloud_name="...", api_key="...", api_secret="...")

@router.post("/upload-image")
async def upload_image(
    file: UploadFile = File(...),
    test_id: str = Form(None),
    admin: User = Depends(get_current_admin_user)
) -> Any:
    """
    Upload an image for inline use in explanations or questions to Cloudinary.
    Returns the Cloudinary CDN secure URL.
    """
    if not os.environ.get("CLOUDINARY_URL"):
        raise HTTPException(status_code=500, detail="CLOUDINARY_URL environment variable is not set. Please configure it in Railway/Render or your .env file.")

    try:
        content = await file.read()
        # Upload directly from bytes to Cloudinary
        folder_path = f"pariksha365_questions/{test_id}" if test_id else "pariksha365_questions/unlinked"
        result = cloudinary.uploader.upload(
            content,
            folder=folder_path, 
            resource_type="image"
        )
        return {"url": result.get("secure_url")}
    except Exception as e:
        print(f"Cloudinary Upload Error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload image to Cloudinary: {str(e)}")


@router.post("/notes/upload")
async def upload_notes_pdf(
    file: UploadFile = File(...),
    slug: str = Form(..., description="Short URL-safe identifier, e.g. 'gk_static_2026'"),
    title: str = Form(..., description="Human-readable title shown to students"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    """Upload a study-notes PDF to R2 and register it in the database.

    The slug becomes the book_id in the download URL:
      GET /api/v1/payments/notes/file/{slug}
    Existing entries with the same slug are updated (upsert).
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    safe_slug = slug.strip().lower().replace(" ", "_")
    if not safe_slug:
        raise HTTPException(status_code=400, detail="slug must not be empty")

    pdf_bytes = await file.read()

    try:
        r2_url = r2_storage.upload_notes_pdf(safe_slug, pdf_bytes)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"R2 upload failed: {e}")

    from sqlalchemy import select
    existing = (await db.execute(
        select(Note).where(Note.slug == safe_slug)
    )).scalars().first()

    if existing:
        existing.title = title
        existing.file_url = r2_url
        existing.is_visible = True
    else:
        db.add(Note(file_url=r2_url, title=title, slug=safe_slug, is_visible=True))

    await db.commit()
    return {"status": "ok", "slug": safe_slug, "r2_url": r2_url}


# --- Notes enablement (admin controls which study-notes books students can use) ---
import json as _json
from pathlib import Path as _Path

_NOTES_DIR = _Path(__file__).resolve().parent.parent.parent / "seeds" / "study_notes" / "_build"
_NOTES_OUT_DIR = _NOTES_DIR / "out"
_NOTES_MANIFEST_FILE = _NOTES_DIR / "manifest.json"


def _manifest_books() -> list[dict]:
    if not _NOTES_MANIFEST_FILE.exists():
        return []
    try:
        return _json.loads(_NOTES_MANIFEST_FILE.read_text()).get("books", [])
    except Exception:
        return []


class NoteVisibilityUpdate(BaseModel):
    is_enabled: bool


@router.get("/notes")
async def admin_list_notes(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    """List every study-notes book with its enabled state so the admin can turn each
    on/off. Locally-built (manifest) books are auto-registered as DB rows the first time
    this is called, disabled by default — the admin must explicitly enable them."""
    from sqlalchemy import select as _select

    existing = {
        n.slug: n for n in (await db.execute(
            _select(Note).where(Note.slug.isnot(None))
        )).scalars().all()
    }

    # Auto-register manifest books (disabled by default) so they are togglable.
    created = 0
    for book in _manifest_books():
        slug = book.get("id")
        if not slug or slug in existing:
            continue
        note = Note(
            file_url=f"local:{slug}",
            title=book.get("title", slug),
            slug=slug,
            is_visible=False,
        )
        db.add(note)
        existing[slug] = note
        created += 1
    if created:
        await db.commit()

    out_map = {b.get("id"): b.get("out") for b in _manifest_books() if b.get("id") and b.get("out")}
    out = []
    for slug, note in existing.items():
        _out = out_map.get(slug)
        is_local = (_NOTES_OUT_DIR / _out).exists() if _out else (_NOTES_OUT_DIR / f"{slug}.pdf").exists()
        out.append({
            "slug": slug,
            "title": note.title or slug,
            "is_enabled": bool(note.is_visible),
            "source": "local" if is_local else "uploaded",
        })
    out.sort(key=lambda x: x["title"].lower())
    return {"notes": out, "count": len(out)}


@router.put("/notes/{slug}/visibility")
async def admin_set_note_visibility(
    slug: str,
    body: NoteVisibilityUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user),
) -> Any:
    """Enable or disable a study-notes book for students (app + web)."""
    from sqlalchemy import select as _select

    safe_slug = slug.strip().lower()
    note = (await db.execute(
        _select(Note).where(Note.slug == safe_slug)
    )).scalars().first()
    if not note:
        # Register from manifest on the fly if it is a known local book.
        book = next((b for b in _manifest_books() if b.get("id") == safe_slug), None)
        if not book:
            raise HTTPException(status_code=404, detail="Note not found")
        note = Note(file_url=f"local:{safe_slug}", title=book.get("title", safe_slug), slug=safe_slug)
        db.add(note)

    note.is_visible = body.is_enabled
    await db.commit()
    return {"slug": safe_slug, "is_enabled": bool(note.is_visible)}

