"""increase_description_column_size

Revision ID: b6ff4e86a158
Revises: f6acf492a61e
Create Date: 2023-11-19 12:57:41.367812

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'b6ff4e86a158'
down_revision: Union[str, None] = 'f6acf492a61e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###    
    op.alter_column('jobs', 'description',
               existing_type=mysql.VARCHAR(length=2000),
               type_=sa.String(length=10000),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('applicants_id', 'skills', ['applicant_id'], unique=False)
    op.alter_column('jobs', 'description',
               existing_type=sa.String(length=10000),
               type_=mysql.VARCHAR(length=2000),
               existing_nullable=True)
    op.create_index('applicants_id', 'experience', ['applicant_id'], unique=False)
    op.create_index('applicants_id', 'education', ['applicant_id'], unique=False)
    # ### end Alembic commands ###