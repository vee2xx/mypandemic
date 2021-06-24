"""add role to users

Revision ID: 60d2408ca953
Revises: 8b4b2524934f
Create Date: 2021-01-02 21:22:55.630331

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '60d2408ca953'
down_revision = '8b4b2524934f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('role', sa.Integer))
    op.add_column('users', sa.Column('password', sa.Unicode(200)))

def downgrade():
    op.drop_column('users', 'role')
    op.drop_column('users', 'password')
