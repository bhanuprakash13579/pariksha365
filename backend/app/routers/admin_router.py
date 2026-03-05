from typing import Any, List
from fastapi import APIRouter, Depends, UploadFile, File, Query, Form
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.schemas.test_schema import TestSeriesCreate, TestSeriesResponse, SectionCreate, SectionResponse
from app.schemas.question_schema import QuestionCreate, QuestionResponse
from app.services import test_series_service, pdf_scraper_service, gemini_service, admin_analytics_service

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

