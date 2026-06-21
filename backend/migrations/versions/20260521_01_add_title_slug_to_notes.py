"""add title and slug to notes

Revision ID: 20260521_01
Revises: 20260424_01
Create Date: 2026-05-21
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260521_01"
down_revision: Union[str, Sequence[str], None] = "20260424_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("notes", sa.Column("title", sa.String(), nullable=True))
    op.add_column("notes", sa.Column("slug", sa.String(), nullable=True))
    op.create_index("ix_notes_slug", "notes", ["slug"])


def downgrade() -> None:
    op.drop_index("ix_notes_slug", table_name="notes")
    op.drop_column("notes", "slug")
    op.drop_column("notes", "title")
