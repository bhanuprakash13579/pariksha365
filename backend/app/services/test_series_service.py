from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from fastapi import HTTPException
from app.models.test_series import TestSeries
from app.models.section import Section
from app.models.question import Question
from app.schemas.test_schema import TestSeriesCreate, TestSeriesUpdate, SectionCreate
from app.schemas.question_schema import QuestionCreate
from app.models.attempt import Attempt
from sqlalchemy import update, delete
import cloudinary
import cloudinary.api

async def create_test_series(db: AsyncSession, test_in: TestSeriesCreate) -> TestSeries:
    db_test = TestSeries(**test_in.model_dump())
    db.add(db_test)
    await db.commit()
    await db.refresh(db_test)
    return db_test

async def get_test_series_list(db: AsyncSession, category: Optional[str] = None, is_published: Optional[bool] = None) -> List[TestSeries]:
    stmt = select(TestSeries).options(selectinload(TestSeries.sections))
    if category:
        stmt = stmt.where(TestSeries.category == category)
    if is_published is not None:
        stmt = stmt.where(TestSeries.is_published == is_published)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_test_series_by_id(db: AsyncSession, test_id: uuid.UUID) -> TestSeries:
    stmt = select(TestSeries).options(
        selectinload(TestSeries.sections)
        .selectinload(Section.questions)
    ).where(TestSeries.id == test_id)
    result = await db.execute(stmt)
    test = result.scalars().first()
    if not test:
        raise HTTPException(status_code=404, detail="Test series not found")
    return test

async def create_section(db: AsyncSession, test_id: uuid.UUID, section_in: SectionCreate) -> Section:
    db_section = Section(test_series_id=test_id, **section_in.model_dump())
    db.add(db_section)
    await db.commit()
    await db.refresh(db_section)
    return db_section

async def create_question(db: AsyncSession, section_id: uuid.UUID, question_in: QuestionCreate) -> Question:
    q_data = question_in.model_dump()
    db_question = Question(section_id=section_id, **q_data)
    db.add(db_question)
    
    await db.commit()
    await db.refresh(db_question)
    return db_question

from app.schemas.test_schema import TestSeriesBulkCreate

async def create_test_series_bulk(db: AsyncSession, test_in: TestSeriesBulkCreate) -> TestSeries:
    test_data = test_in.model_dump(exclude={"sections", "price", "is_free", "validity_days", "is_daily_quiz"}, exclude_none=True)
    # Allow ID to be explicitly set from the frontend (e.g. for linking images to a draft test folder)
    db_test = TestSeries(**test_data)
    db.add(db_test)
    await db.flush() # Get ID
    
    for s_idx, sec_in in enumerate(test_in.sections):
        sec_data = sec_in.model_dump(exclude={"questions", "title"}, exclude_none=True)
        if "id" in sec_data:
            sec_data.pop("id")
        sec_data["name"] = sec_in.title
        sec_data["order_num"] = s_idx
        db_sec = Section(test_series_id=db_test.id, **sec_data)
        db.add(db_sec)
        await db.flush()
        
        for q_idx, q_in in enumerate(sec_in.questions):
            q_data = q_in.model_dump(exclude_none=True)
            if "id" in q_data:
                q_data.pop("id")
            q_data["order_num"] = q_idx
            db_q = Question(section_id=db_sec.id, **q_data)
            db.add(db_q)

    await db.commit()
    return await get_test_series_by_id(db, db_test.id)

async def update_test_series_full(db: AsyncSession, test_id: uuid.UUID, test_in: TestSeriesBulkCreate) -> TestSeries:
    """
    Carefully updates a Test Series, its Sections, Questions, and Options without deleting
    the entire tree. This preserves UUIDs so that existing UserAnswers are not orphaned.
    """
    # 1. Fetch existing test with full eager loading
    db_test = await get_test_series_by_id(db, test_id)
    
    # 2. Update top-level test properties
    test_update_data = test_in.model_dump(exclude={"sections", "id", "price", "is_free", "validity_days", "is_daily_quiz"}, exclude_unset=True)
    for key, value in test_update_data.items():
        setattr(db_test, key, value)
        
    # 3. Synchronize Sections
    incoming_sec_ids = [s.id for s in test_in.sections if s.id]
    
    # Delete missing sections
    for existing_sec in list(db_test.sections):
        if existing_sec.id not in incoming_sec_ids:
            # Sever UserAnswer ties to avoid ForeignKeyViolation
            for q in existing_sec.questions:
                await db.execute(delete(UserAnswer).where(UserAnswer.question_id == q.id))
            await db.delete(existing_sec)
            db_test.sections.remove(existing_sec)
            
    for s_idx, sec_in in enumerate(test_in.sections):
        if sec_in.id:
            # Update existing section
            existing_sec = next((s for s in db_test.sections if s.id == sec_in.id), None)
            if existing_sec:
                existing_sec.name = sec_in.title
                existing_sec.time_limit_minutes = sec_in.time_limit_minutes
                existing_sec.marks_per_question = sec_in.marks_per_question
                existing_sec.order_num = s_idx
                
                # Synchronize Questions internally
                incoming_q_ids = [q.id for q in sec_in.questions if q.id]
                for existing_q in list(existing_sec.questions):
                    if existing_q.id not in incoming_q_ids:
                        await db.execute(delete(UserAnswer).where(UserAnswer.question_id == existing_q.id))
                        await db.delete(existing_q)
                        existing_sec.questions.remove(existing_q)
                        
                for q_idx, q_in in enumerate(sec_in.questions):
                    if q_in.id:
                        existing_q = next((q for q in existing_sec.questions if q.id == q_in.id), None)
                        if existing_q:
                            existing_q.question_text = q_in.question_text
                            existing_q.image_url = q_in.image_url
                            existing_q.explanation = q_in.explanation
                            existing_q.difficulty = q_in.difficulty
                            existing_q.subject = q_in.subject
                            existing_q.topic = q_in.topic
                            existing_q.topic_code = q_in.topic_code
                            existing_q.order_num = q_idx
                            
                            # Options is now JSONB Array. Replace entirely.
                            existing_q.options = [o.model_dump(exclude_none=True) for o in q_in.options]
                                
                    else:
                        # Insert entirely new question
                        q_data = q_in.model_dump(exclude={"id"})
                        q_data["order_num"] = q_idx
                        new_q = Question(section_id=existing_sec.id, **q_data)
                        db.add(new_q)
        else:
            # Insert entirely new section
            sec_data = sec_in.model_dump(exclude={"questions", "title", "id"})
            sec_data["name"] = sec_in.title
            sec_data["order_num"] = s_idx
            new_sec = Section(test_series_id=db_test.id, **sec_data)
            db.add(new_sec)
            await db.flush()
            for q_idx, q_in in enumerate(sec_in.questions):
                q_data = q_in.model_dump(exclude={"id"})
                q_data["order_num"] = q_idx
                new_q = Question(section_id=new_sec.id, **q_data)
                db.add(new_q)

    await db.commit()
    return await get_test_series_by_id(db, db_test.id)

async def delete_test_series(db: AsyncSession, test_id: uuid.UUID):
    stmt = select(TestSeries).where(TestSeries.id == test_id)
    result = await db.execute(stmt)
    test = result.scalars().first()
    
    if not test:
        raise HTTPException(status_code=404, detail="Test series not found")
        
    # Prevent deletion if the test has been attempted
    attempt_check_stmt = select(Attempt).where(Attempt.test_series_id == test_id).limit(1)
    has_attempts = await db.execute(attempt_check_stmt)
    if has_attempts.scalars().first() is not None:
        raise HTTPException(status_code=400, detail="Cannot delete this test because it has existing user attempts. Please unpublish it or edit it instead.")
    
    # 1. Safely delete ONLY the Cloudinary images linked directly to this test's unique isolated folder
    try:
        folder_path = f"pariksha365_questions/{test_id}"
        cloudinary.api.delete_resources_by_prefix(f"{folder_path}/")
        cloudinary.api.delete_folder(folder_path)
    except Exception as e:
        print(f"Error sweeping Cloudinary folder {folder_path} during test deletion: {e}")

    await db.delete(test)
    await db.commit()
    return {"message": "Test series and associated images deleted successfully"}

from app.services.r2_storage_service import r2_storage
from app.schemas.test_schema import TestSeriesFullResponse

async def publish_test_series(db: AsyncSession, test_id: uuid.UUID) -> TestSeries:
    stmt = select(TestSeries).options(
        selectinload(TestSeries.sections)
        .selectinload(Section.questions)
    ).where(TestSeries.id == test_id)
    
    result = await db.execute(stmt)
    test = result.scalars().first()
    if not test:
        raise HTTPException(status_code=404, detail="Test series not found")
        
    # Serialize the complete structure using Pydantic
    schema_dump = TestSeriesFullResponse.model_validate(test).model_dump(mode='json')
    
    try:
        # Upload the JSON document to Cloudflare R2
        cdn_url = await r2_storage.upload_test_json(str(test.id), schema_dump)
        test.cdn_url = cdn_url
    except Exception as e:
        print(f"Failed to upload to R2 CDN: {e}")
        # Soft-fail: the test publishes but lacks CDN URL
        pass
    
    test.is_published = True
    await db.commit()
    await db.refresh(test)
    return test
