"""add points and stars to users

Revision ID: 87bcddea8fbd
Revises: 
Create Date: 2026-03-04 21:46:23.838713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '87bcddea8fbd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('points', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('users', sa.Column('stars', sa.Integer(), nullable=True, server_default='0'))


def downgrade() -> None:
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('stars')
        batch_op.drop_column('points')
