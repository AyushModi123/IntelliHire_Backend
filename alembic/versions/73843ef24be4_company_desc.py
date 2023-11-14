"""company_desc

Revision ID: 73843ef24be4
Revises: e7483dd4ef1b
Create Date: 2023-11-14 22:59:19.650734

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '73843ef24be4'
down_revision: Union[str, None] = 'e7483dd4ef1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('employers', sa.Column('company_desc', sa.VARCHAR(1000), nullable=False))

def downgrade() -> None:
    op.drop_column('employers', 'company_desc')
