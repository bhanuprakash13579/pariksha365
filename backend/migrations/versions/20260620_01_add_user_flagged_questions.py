"""add user_flagged_questions table

Revision ID: 20260620_01
Revises: 20260618_01
Create Date: 2026-06-20
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "20260620_01"
down_revision: Union[str, None] = "20260618_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_flagged_questions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", UUID(as_uuid=True),
                  sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_source", sa.String(32), nullable=False),
        sa.Column("question_id", sa.String(36), nullable=False),
        sa.Column("user_note", sa.Text(), nullable=True),
        sa.Column("flagged_at", sa.DateTime(timezone=True),
                  server_default=sa.text("now()"), nullable=False),
    )
    op.create_unique_constraint(
        "uq_flagged_user_source_question",
        "user_flagged_questions",
        ["user_id", "question_source", "question_id"],
    )
    op.create_index("ix_flagged_user_source", "user_flagged_questions",
                    ["user_id", "question_source"])
    op.create_index("ix_user_flagged_questions_user_id", "user_flagged_questions",
                    ["user_id"])


def downgrade() -> None:
    op.drop_table("user_flagged_questions")
