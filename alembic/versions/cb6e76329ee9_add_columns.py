"""add columns

Revision ID: cb6e76329ee9
Revises: 17a24d61b06a
Create Date: 2023-11-18 14:38:36.008410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb6e76329ee9'
down_revision: Union[str, None] = '17a24d61b06a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('applicant_jobs', sa.Column('resume', sa.Boolean(), nullable=True))
    op.add_column('applicant_jobs', sa.Column('job_fit', sa.Boolean(), nullable=True))
    op.add_column('applicant_jobs', sa.Column('aptitude', sa.Boolean(), nullable=True))
    op.add_column('applicant_jobs', sa.Column('skill', sa.Boolean(), nullable=True))
    op.add_column('applicant_jobs', sa.Column('completed', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('applicants_id', 'skills', ['applicant_id'], unique=False)
    op.create_index('applicants_id', 'experience', ['applicant_id'], unique=False)
    op.create_index('applicants_id', 'education', ['applicant_id'], unique=False)
    op.drop_column('applicant_jobs', 'completed')
    op.drop_column('applicant_jobs', 'skill')
    op.drop_column('applicant_jobs', 'aptitude')
    op.drop_column('applicant_jobs', 'job_fit')
    op.drop_column('applicant_jobs', 'resume')
    # ### end Alembic commands ###
