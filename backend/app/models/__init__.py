from app.core.database import Base
from app.models.role import Role
from app.models.user import User
from app.models.test_series import TestSeries, TestType
from app.models.section import Section
from app.models.question import Question
from app.models.attempt import Attempt
from app.models.user_answer import UserAnswer
from app.models.result import Result
from app.models.enrollment import Enrollment
from app.models.notes import Note
from app.models.payment import Payment
from app.models.course import Course
from app.models.course_folder import CourseFolder
from app.models.folder_test import FolderTest
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.exam_stage import ExamStage
from app.models.exam_stage_purchase import ExamStagePurchase
from app.models.exam_pattern import ExamPattern, SectionPattern
from app.models.quiz_pool import QuizQuestion, QuizAttempt, UserWeakTopic, UserStreak, UserTopicMastery
from app.models.taxonomy import SubjectTaxonomy
from app.models.private_module import (
    PrivateModule, PrivateModuleQuestion, PrivateModuleAccess,
    PrivateModuleAttempt, PrivateModuleWeakTopic,
)
from app.models.notes_purchase import NotesPurchase
from app.models.flagged_question import UserFlaggedQuestion

# Expose Base and Models for Alembic metadata
__all__ = [
    "Base",
    "Role",
    "User",
    "TestSeries",
    "TestType",
    "Section",
    "Question",
    "Attempt",
    "UserAnswer",
    "Result",
    "Enrollment",
    "Note",
    "Payment",
    "Course",
    "CourseFolder",
    "FolderTest",
    "Category",
    "SubCategory",
    "ExamStage",
    "ExamStagePurchase",
    "ExamPattern",
    "SectionPattern",
    "QuizQuestion",
    "QuizAttempt",
    "UserWeakTopic",
    "UserStreak",
    "UserTopicMastery",
    "SubjectTaxonomy",
    "PrivateModule",
    "PrivateModuleQuestion",
    "PrivateModuleAccess",
    "PrivateModuleAttempt",
    "PrivateModuleWeakTopic",
    "NotesPurchase",
    "UserFlaggedQuestion",
]
