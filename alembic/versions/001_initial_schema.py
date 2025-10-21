"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'jobs',
        sa.Column('job_id', sa.String(), nullable=False),
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('coupon_code', sa.String(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('job_start_time', sa.DateTime(), nullable=False),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('job_id')
    )
    op.create_index(op.f('ix_jobs_site_id'), 'jobs', ['site_id'], unique=False)
    op.create_index(op.f('ix_jobs_coupon_code'), 'jobs', ['coupon_code'], unique=False)
    op.create_index(op.f('ix_jobs_created_at'), 'jobs', ['created_at'], unique=False)

    op.create_table(
        'coupon_stats',
        sa.Column('site_id', sa.Integer(), nullable=False),
        sa.Column('coupon_code', sa.String(), nullable=False),
        sa.Column('run_count', sa.Integer(), nullable=False),
        sa.Column('last_run_at', sa.DateTime(), nullable=False),
        sa.Column('last_job_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('site_id', 'coupon_code')
    )
    op.create_index(op.f('ix_coupon_stats_last_run_at'), 'coupon_stats', ['last_run_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_coupon_stats_last_run_at'), table_name='coupon_stats')
    op.drop_table('coupon_stats')
    op.drop_index(op.f('ix_jobs_created_at'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_coupon_code'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_site_id'), table_name='jobs')
    op.drop_table('jobs')
