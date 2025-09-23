"""merge migrations

Revision ID: d03d7f4dc8e4
Revises: 05c66172341f, 39dd0224c274
Create Date: 2025-09-21 22:08:45.217008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd03d7f4dc8e4'
down_revision = ('05c66172341f', '39dd0224c274')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
