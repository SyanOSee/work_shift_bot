"""Merge multiple heads

Revision ID: d26b0a612494
Revises: d8efda157d0c
Create Date: 2023-12-29 21:55:08.989947

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd26b0a612494'
down_revision: Union[str, None] = 'd8efda157d0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
