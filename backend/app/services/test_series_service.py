from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import uuid
from fastapi import HTTPException
from app.models.test_series import TestSeries
from app.models.section import Section
from app.models.question import Question
from app.models.option import Option
from app.schemas.test_schema import TestSeriesCreate, TestSeriesUpdate, SectionCreate
from app.schemas.question_schema import QuestionCreate

async def create_test_series(db: AsyncSession, test_in: TestSeriesCreate) -> TestSeries:
    db_test = TestSeries(**test_in.model_dump())
    db.add(db_test)
    await db.commit()
    await db.refresh(db_test)
    return db_test

async def get_test_series_list(db: AsyncSession, category: Optional[str] = None, is_published: Optional[bool] = None) -> List[TestSeries]:
    stmt = select(TestSeries)
    if category:
        stmt = stmt.where(TestSeries.category == category)
    if is_published is not None:
        stmt = stmt.where(TestSeries.is_published == is_published)
    result = await db.execute(stmt)
    return result.scalars().all()

async def get_test_series_by_id(db: AsyncSession, test_id: uuid.UUID) -> TestSeries:
    stmt = select(TestSeries).options(selectinload(TestSeries.sections)).where(TestSeries.id == test_id)
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
    q_data = question_in.model_dump(exclude={"options"})
    db_question = Question(section_id=section_id, **q_data)
    db.add(db_question)
    await db.flush() # Flush to get id

    for opt in question_in.options:
        db_option = Option(question_id=db_question.id, **opt.model_dump())
        db.add(db_option)
    
    await db.commit()
    await db.refresh(db_question)
    return db_question

from app.schemas.test_schema import TestSeriesBulkCreate

async def create_test_series_bulk(db: AsyncSession, test_in: TestSeriesBulkCreate) -> TestSeries:
    test_data = test_in.model_dump(exclude={"sections"})
    db_test = TestSeries(**test_data)
    db.add(db_test)
    await db.flush() # Get ID
    
    for s_idx, sec_in in enumerate(test_in.sections):
        sec_data = sec_in.model_dump(exclude={"questions"})
        db_sec = Section(test_series_id=db_test.id, order_index=s_idx+1, **sec_data)
        db.add(db_sec)
        await db.flush()
        
        for q_idx, q_in in enumerate(sec_in.questions):
            q_data = q_in.model_dump(exclude={"options"})
            db_q = Question(section_id=db_sec.id, order_index=q_idx+1, **q_data)
            db.add(db_q)
            await db.flush()
            
            for o_in in q_in.options:
                db_opt = Option(question_id=db_q.id, **o_in.model_dump())
                db.add(db_opt)

    await db.commit()
    await db.refresh(db_test)
    return db_test
