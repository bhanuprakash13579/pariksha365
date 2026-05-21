"""add diagram_svg to questions and quiz_questions

Revision ID: 20260521_01
Revises: 20260424_01
Create Date: 2026-05-21
"""
from typing import Union, Sequence
import sqlalchemy as sa
from alembic import op

revision: str = "20260521_01"
down_revision: Union[str, Sequence[str], None] = "20260424_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("diagram_svg", sa.Text(), nullable=True))
    op.add_column("questions", sa.Column("explanation_svg", sa.Text(), nullable=True))
    op.add_column("quiz_questions", sa.Column("diagram_svg", sa.Text(), nullable=True))
    op.add_column("quiz_questions", sa.Column("explanation_svg", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("quiz_questions", "explanation_svg")
    op.drop_column("quiz_questions", "diagram_svg")
    op.drop_column("questions", "explanation_svg")
    op.drop_column("questions", "diagram_svg")
