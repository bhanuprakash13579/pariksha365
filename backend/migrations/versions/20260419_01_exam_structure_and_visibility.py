"""exam_structure_and_visibility

Introduces the exam-structure backbone that lets admins gate-release content per
body/exam/stage and that informs mock-test generation + the test-taker timer UI.

Changes:
  * ``categories``     — adds ``description`` (text) and ``is_enabled`` (bool,
                          default False) so admins must explicitly release a
                          body (Banks/SSC/RRB/...) before it appears to students.
  * ``subcategories``  — adds ``slug``, ``description``, ``is_enabled`` + a
                          ``(category_id, slug)`` unique constraint.
  * ``exam_stages``    — NEW. One row per stage (Prelims, Mains, Tier 1, Tier 2,
                          CBT 1, CBT 2, ...) under a subcategory; carries its
                          own visibility flag.
  * ``exam_patterns``  — NEW. Blueprint (duration, total Qs, negative marking,
                          sectional-timing flag) for a stage.
  * ``section_patterns`` — NEW. Per-section breakdown inside a pattern
                          (name, subject, question count, per-section duration,
                          marks per question).
  * ``test_series``    — adds ``test_type`` (MOCK/PYQ enum, default MOCK),
                          ``exam_stage_id`` FK, and PYQ-provenance columns
                          (``source_pdf_path``, ``paper_date``, ``paper_shift``).

All new visibility flags default to ``False`` so no existing data leaks to
students on first run; the admin must opt-in to surface any body/exam/stage.

Revision ID: 20260419_01
Revises: 87bcddea8fbd
Create Date: 2026-04-19
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260419_01"
down_revision: Union[str, Sequence[str], None] = "87bcddea8fbd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. categories: description + is_enabled
    op.add_column("categories", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "categories",
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    op.create_index("ix_categories_is_enabled", "categories", ["is_enabled"])

    # 2. subcategories: slug + description + is_enabled + unique(category_id, slug)
    op.add_column("subcategories", sa.Column("slug", sa.String(), nullable=True))
    op.add_column("subcategories", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "subcategories",
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )
    # Backfill slug for existing rows from lower(name), replacing whitespace with hyphens.
    op.execute(
        "UPDATE subcategories SET slug = LOWER(REGEXP_REPLACE(name, '[^a-zA-Z0-9]+', '-', 'g')) "
        "WHERE slug IS NULL"
    )
    op.alter_column("subcategories", "slug", nullable=False)
    op.create_index("ix_subcategories_is_enabled", "subcategories", ["is_enabled"])
    op.create_unique_constraint(
        "uq_subcategory_cat_slug", "subcategories", ["category_id", "slug"]
    )

    # 3. exam_stages: NEW
    op.create_table(
        "exam_stages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "subcategory_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("subcategories.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("subcategory_id", "slug", name="uq_exam_stage_subcat_slug"),
    )
    op.create_index("ix_exam_stages_id", "exam_stages", ["id"])
    op.create_index("ix_exam_stages_subcategory_id", "exam_stages", ["subcategory_id"])
    op.create_index("ix_exam_stages_is_enabled", "exam_stages", ["is_enabled"])

    # 4. exam_patterns: NEW (1:1 with exam_stages)
    op.create_table(
        "exam_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "exam_stage_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exam_stages.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("total_duration_minutes", sa.Integer(), nullable=False),
        sa.Column("total_questions", sa.Integer(), nullable=False),
        sa.Column("total_marks", sa.Float(), nullable=False),
        sa.Column(
            "negative_mark_per_wrong", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "has_sectional_timing",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
        ),
    )
    op.create_index("ix_exam_patterns_id", "exam_patterns", ["id"])
    op.create_index(
        "ix_exam_patterns_exam_stage_id", "exam_patterns", ["exam_stage_id"]
    )

    # 5. section_patterns: NEW (many per exam_pattern)
    op.create_table(
        "section_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "exam_pattern_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exam_patterns.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column(
            "marks_per_question", sa.Float(), nullable=False, server_default="1.0"
        ),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_section_patterns_id", "section_patterns", ["id"])
    op.create_index(
        "ix_section_patterns_exam_pattern_id",
        "section_patterns",
        ["exam_pattern_id"],
    )
    op.create_index("ix_section_patterns_subject", "section_patterns", ["subject"])

    # 6. test_series: add exam_stage_id, test_type, PYQ provenance columns.
    # Create the enum type first (postgres-specific).
    test_type_enum = postgresql.ENUM("MOCK", "PYQ", name="test_type_enum", create_type=False)
    test_type_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "test_series",
        sa.Column(
            "exam_stage_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("exam_stages.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.add_column(
        "test_series",
        sa.Column(
            "test_type",
            test_type_enum,
            nullable=False,
            server_default="MOCK",
        ),
    )
    op.add_column("test_series", sa.Column("source_pdf_path", sa.String(), nullable=True))
    op.add_column("test_series", sa.Column("paper_date", sa.Date(), nullable=True))
    op.add_column("test_series", sa.Column("paper_shift", sa.String(), nullable=True))
    op.create_index("ix_test_series_exam_stage_id", "test_series", ["exam_stage_id"])
    op.create_index("ix_test_series_test_type", "test_series", ["test_type"])


def downgrade() -> None:
    # test_series: drop new columns + enum
    op.drop_index("ix_test_series_test_type", table_name="test_series")
    op.drop_index("ix_test_series_exam_stage_id", table_name="test_series")
    op.drop_column("test_series", "paper_shift")
    op.drop_column("test_series", "paper_date")
    op.drop_column("test_series", "source_pdf_path")
    op.drop_column("test_series", "test_type")
    op.drop_column("test_series", "exam_stage_id")
    test_type_enum = postgresql.ENUM("MOCK", "PYQ", name="test_type_enum")
    test_type_enum.drop(op.get_bind(), checkfirst=True)

    # section_patterns
    op.drop_index("ix_section_patterns_subject", table_name="section_patterns")
    op.drop_index("ix_section_patterns_exam_pattern_id", table_name="section_patterns")
    op.drop_index("ix_section_patterns_id", table_name="section_patterns")
    op.drop_table("section_patterns")

    # exam_patterns
    op.drop_index("ix_exam_patterns_exam_stage_id", table_name="exam_patterns")
    op.drop_index("ix_exam_patterns_id", table_name="exam_patterns")
    op.drop_table("exam_patterns")

    # exam_stages
    op.drop_index("ix_exam_stages_is_enabled", table_name="exam_stages")
    op.drop_index("ix_exam_stages_subcategory_id", table_name="exam_stages")
    op.drop_index("ix_exam_stages_id", table_name="exam_stages")
    op.drop_table("exam_stages")

    # subcategories: drop added columns + constraint
    op.drop_constraint("uq_subcategory_cat_slug", "subcategories", type_="unique")
    op.drop_index("ix_subcategories_is_enabled", table_name="subcategories")
    op.drop_column("subcategories", "is_enabled")
    op.drop_column("subcategories", "description")
    op.drop_column("subcategories", "slug")

    # categories
    op.drop_index("ix_categories_is_enabled", table_name="categories")
    op.drop_column("categories", "is_enabled")
    op.drop_column("categories", "description")
