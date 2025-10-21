"""rename base_url to domain

Revision ID: 003
Revises: 002
Create Date: 2025-10-19 12:00:00.000000

"""
from alembic import op

revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('sites', 'base_url', new_column_name='domain')


def downgrade() -> None:
    op.alter_column('sites', 'domain', new_column_name='base_url')
