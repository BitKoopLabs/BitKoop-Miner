"""add sites table

Revision ID: 002
Revises: 001
Create Date: 2025-10-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'sites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('base_url', sa.String(), nullable=False),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('miner_hotkey', sa.String(), nullable=True),
        sa.Column('api_url', sa.String(), nullable=True),
        sa.Column('total_coupon_slots', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sites_id'), 'sites', ['id'], unique=False)
    op.create_index(op.f('ix_sites_created_at'), 'sites', ['created_at'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_sites_created_at'), table_name='sites')
    op.drop_index(op.f('ix_sites_id'), table_name='sites')
    op.drop_table('sites')
