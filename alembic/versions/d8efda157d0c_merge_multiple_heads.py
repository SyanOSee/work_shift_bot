"""Merge multiple heads

Revision ID: d8efda157d0c
Revises: 115844109fe1
Create Date: 2023-12-29 21:54:49.754732

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8efda157d0c'
down_revision: Union[str, None] = '115844109fe1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
