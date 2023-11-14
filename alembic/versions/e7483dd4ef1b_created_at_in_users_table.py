"""created_at in users table

Revision ID: e7483dd4ef1b
Revises: 7cb517d0ddd5
Create Date: 2023-11-14 14:41:14.428802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7483dd4ef1b'
down_revision: Union[str, None] = '7cb517d0ddd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('users', sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False))

def downgrade() -> None:
    op.drop_column('users', 'created_at')