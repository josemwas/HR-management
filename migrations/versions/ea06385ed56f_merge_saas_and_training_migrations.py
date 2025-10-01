"""merge saas and training migrations

Revision ID: ea06385ed56f
Revises: 20251001_160142, saas_migration_001
Create Date: 2025-10-01 16:21:45.298508

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea06385ed56f'
down_revision = ('20251001_160142', 'saas_migration_001')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
