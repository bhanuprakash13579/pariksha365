"""private_modules — gated question banks with per-email whitelist

Introduces five new tables that together form a self-contained question
universe (e.g. EPFO APFC bank) isolated from the main quiz pool:

  * ``private_modules``              — one row per gated bank.
  * ``private_module_questions``     — questions scoped to a module.
  * ``private_module_access``        — (module, email) whitelist entries.
  * ``private_module_attempts``      — user answers, used for dedup + weak signal.
  * ``private_module_weak_topics``   — module-scoped weak-topic tracker so
                                        signals never leak into the main pool.

Revision ID: 20260424_01
Revises: 20260419_01
Create Date: 2026-04-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260424_01"
down_revision: Union[str, Sequence[str], None] = "20260419_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. private_modules
    op.create_table(
        "private_modules",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("slug", name="uq_private_modules_slug"),
    )
    op.create_index("ix_private_modules_id", "private_modules", ["id"])
    op.create_index("ix_private_modules_slug", "private_modules", ["slug"])

    # 2. private_module_questions
    op.create_table(
        "private_module_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "module_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("private_modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("qnum", sa.Integer(), nullable=True),
        sa.Column("section", sa.String(), nullable=True),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("topic_code", sa.String(), nullable=False),
        sa.Column("difficulty", sa.String(), nullable=False, server_default="MEDIUM"),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSON(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_private_module_questions_id", "private_module_questions", ["id"])
    op.create_index("ix_private_module_questions_module_id", "private_module_questions", ["module_id"])
    op.create_index("ix_private_module_questions_subject", "private_module_questions", ["subject"])
    op.create_index("ix_private_module_questions_topic", "private_module_questions", ["topic"])
    op.create_index("ix_private_module_questions_topic_code", "private_module_questions", ["topic_code"])
    op.create_index("ix_priv_mod_q_module_subject_topic", "private_module_questions",
                    ["module_id", "subject", "topic_code"])

    # 3. private_module_access
    op.create_table(
        "private_module_access",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "module_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("private_modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("note", sa.String(), nullable=True),
        sa.Column(
            "granted_by",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("granted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("module_id", "email", name="uq_private_module_access_module_email"),
    )
    op.create_index("ix_private_module_access_id", "private_module_access", ["id"])
    op.create_index("ix_private_module_access_module_id", "private_module_access", ["module_id"])
    op.create_index("ix_private_module_access_email", "private_module_access", ["email"])

    # 4. private_module_attempts
    op.create_table(
        "private_module_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "module_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("private_modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("private_module_questions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("was_correct", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("attempted_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_private_module_attempts_id", "private_module_attempts", ["id"])
    op.create_index("ix_private_module_attempts_user_id", "private_module_attempts", ["user_id"])
    op.create_index("ix_private_module_attempts_module_id", "private_module_attempts", ["module_id"])
    op.create_index("ix_private_module_attempts_question_id", "private_module_attempts", ["question_id"])

    # 5. private_module_weak_topics
    op.create_table(
        "private_module_weak_topics",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "module_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("private_modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("topic", sa.String(), nullable=True),
        sa.Column("topic_code", sa.String(), nullable=False),
        sa.Column("accuracy", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("total_questions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "module_id", "topic_code",
                            name="uq_private_module_weak_user_mod_code"),
    )
    op.create_index("ix_private_module_weak_topics_id", "private_module_weak_topics", ["id"])
    op.create_index("ix_private_module_weak_topics_user_id", "private_module_weak_topics", ["user_id"])
    op.create_index("ix_private_module_weak_topics_module_id", "private_module_weak_topics", ["module_id"])
    op.create_index("ix_private_module_weak_topics_topic_code", "private_module_weak_topics", ["topic_code"])


def downgrade() -> None:
    op.drop_table("private_module_weak_topics")
    op.drop_table("private_module_attempts")
    op.drop_table("private_module_access")
    op.drop_table("private_module_questions")
    op.drop_table("private_modules")
