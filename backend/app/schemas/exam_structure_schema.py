"""Pydantic schemas for the exam-structure backbone.

Covers the ExamStage / ExamPattern / SectionPattern models plus the visibility-
toggle payloads used by the admin endpoints. Kept in its own module so the
legacy ``category_schema`` stays minimal.
"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# ---- Section pattern -------------------------------------------------------

class SectionPatternBase(BaseModel):
    name: str
    subject: str
    question_count: int = Field(ge=1)
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    marks_per_question: float = 1.0
    order: int = 0


class SectionPatternCreate(SectionPatternBase):
    pass


class SectionPatternOut(SectionPatternBase):
    id: UUID
    exam_pattern_id: UUID
    model_config = ConfigDict(from_attributes=True)


# ---- Exam pattern ----------------------------------------------------------

class ExamPatternBase(BaseModel):
    total_duration_minutes: int = Field(ge=1)
    total_questions: int = Field(ge=1)
    total_marks: float = Field(gt=0)
    negative_mark_per_wrong: float = 0.0
    has_sectional_timing: bool = False
    notes: Optional[str] = None


class ExamPatternCreate(ExamPatternBase):
    """Inline creation payload — section_patterns are created atomically with the pattern."""

    section_patterns: List[SectionPatternCreate] = Field(default_factory=list)


class ExamPatternOut(ExamPatternBase):
    id: UUID
    exam_stage_id: UUID
    section_patterns: List[SectionPatternOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# ---- Exam stage ------------------------------------------------------------

class ExamStageBase(BaseModel):
    name: str
    slug: str
    order: int = 0
    is_enabled: bool = False
    price_inr: int = Field(default=0, ge=0)
    validity_days: int = Field(default=365, ge=1)


class ExamStageCreate(ExamStageBase):
    subcategory_id: UUID
    exam_pattern: Optional[ExamPatternCreate] = None


class ExamStageOut(ExamStageBase):
    id: UUID
    subcategory_id: UUID
    created_at: datetime
    exam_pattern: Optional[ExamPatternOut] = None
    model_config = ConfigDict(from_attributes=True)


class ExamStagePricingUpdate(BaseModel):
    """Admin payload for pricing edit. Both fields required — keeps the admin
    UI honest: if you're changing the price you should think about validity too.
    """
    price_inr: int = Field(ge=0, description="Price in rupees. 0 = free.")
    validity_days: int = Field(ge=1, description="Days of access after purchase.")


class ExamStageAccessOut(BaseModel):
    """Student-facing entitlement check result."""
    exam_stage_id: UUID
    is_free: bool
    has_active_access: bool
    price_inr: int
    validity_days: int
    expires_at: Optional[datetime] = None  # set iff user has an active purchase


class ExamStagePurchaseOut(BaseModel):
    id: UUID
    exam_stage_id: UUID
    amount_paid_inr: int
    validity_days_at_purchase: int
    purchased_at: datetime
    expires_at: datetime
    note: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class AdminGrantPurchaseIn(BaseModel):
    """Admin-only: grant a stage entitlement without real payment (testing,
    support refunds, promo codes). ``note`` is required so the audit trail
    never has a 'why is this here?' row.
    """
    user_id: UUID
    exam_stage_id: UUID
    validity_days: int = Field(ge=1)
    note: str = Field(min_length=3, description="Reason for grant — shown in admin audit.")


# ---- SubCategory and Category (enhanced with new fields) -------------------

class SubCategoryWithStagesOut(BaseModel):
    id: UUID
    category_id: UUID
    name: str
    slug: str
    description: Optional[str] = None
    order: int
    is_enabled: bool
    created_at: datetime
    exam_stages: List[ExamStageOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class CategoryWithStructureOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    icon_name: Optional[str] = None
    image_url: Optional[str] = None
    order: int
    is_enabled: bool
    created_at: datetime
    subcategories: List[SubCategoryWithStagesOut] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


# ---- Published test series (student-facing) --------------------------------

class PublishedTestOut(BaseModel):
    """Lightweight projection of a published TestSeries for the student home
    screen. Only carries what the card UI needs — start the test via
    POST /attempts/start/{id} as usual."""

    id: UUID
    title: str
    test_type: str           # "MOCK" or "PYQ"
    total_questions: Optional[int] = None
    total_duration_minutes: Optional[int] = None
    has_sectional_timing: bool = False
    negative_marking: float = 0.25
    paper_date: Optional[str] = None
    paper_shift: Optional[str] = None
    stage_id: UUID
    stage_name: str
    subcategory_id: UUID
    subcategory_name: str
    category_id: UUID
    category_name: str

    model_config = ConfigDict(from_attributes=True)


# ---- Visibility toggle payloads -------------------------------------------

class VisibilityToggleIn(BaseModel):
    """Admin payload for flipping ``is_enabled`` on Category / SubCategory /
    ExamStage. Using an explicit bool (not a PATCH-style partial) keeps the
    intent unambiguous in audit logs.
    """

    is_enabled: bool


class VisibilityToggleOut(BaseModel):
    id: UUID
    is_enabled: bool
    entity: str  # "category" | "subcategory" | "exam_stage"
