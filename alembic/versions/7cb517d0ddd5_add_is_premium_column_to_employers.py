"""Add is_premium column to employers

Revision ID: 7cb517d0ddd5
Revises: e3f558ad5db8
Create Date: 2023-11-13 23:24:41.460777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cb517d0ddd5'
down_revision: Union[str, None] = 'e3f558ad5db8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('employers', sa.Column('is_premium', sa.Boolean(), server_default=sa.false(), nullable=True))

def downgrade():
    op.drop_column('employers', 'is_premium')
