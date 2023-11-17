"""change column name

Revision ID: e02c7d9d0404
Revises: 01b4c280a790
Create Date: 2023-11-17 16:24:59.449971

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e02c7d9d0404'
down_revision: Union[str, None] = '01b4c280a790'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('education', 'applicants_id', type_=sa.Integer(), new_column_name='applicant_id')
    op.alter_column('experience', 'applicants_id', type_=sa.Integer(), new_column_name='applicant_id')
    op.alter_column('skills', 'applicants_id', type_=sa.Integer(), new_column_name='applicant_id')

def downgrade() -> None:
    pass
