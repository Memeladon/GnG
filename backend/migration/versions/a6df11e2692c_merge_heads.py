"""Merge heads

Revision ID: a6df11e2692c
Revises: b1358dbfd957, bd7196417521
Create Date: 2025-08-23 10:54:16.159904

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6df11e2692c'
down_revision: Union[str, None] = ('b1358dbfd957', 'bd7196417521')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
