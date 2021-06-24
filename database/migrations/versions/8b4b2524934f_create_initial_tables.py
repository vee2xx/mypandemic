"""create stats table

Revision ID: 8b4b2524934f
Revises: 
Create Date: 2021-01-02 20:58:25.946787

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision = '8b4b2524934f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    tables = inspector.get_table_names()

    if 'stats' not in tables:
        op.create_table(
            'stats',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('country', sa.Unicode(200)),
            sa.Column('region', sa.Unicode(200)),
            sa.Column('location', sa.Unicode(200)),
            sa.Column('date', sa.Date),
            sa.Column('confirmed', sa.Integer),
            sa.Column('deaths', sa.Integer),
            sa.Column('recovered', sa.Integer),
            sa.Column('active', sa.Integer),
        )

    if 'deltas' not in tables:
        op.create_table(
            'deltas',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('country', sa.Unicode(200)),
            sa.Column('region', sa.Unicode(200)),
            sa.Column('location', sa.Unicode(200)),
            sa.Column('date', sa.Date),
            sa.Column('new_cases', sa.Integer),
            sa.Column('percent_delta', sa.Float),
        )

    if 'country_regions' not in tables:
        op.create_table(
            'country_regions',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('country', sa.Unicode(200)),
            sa.Column('region', sa.Unicode(200)),
        )


    if 'users' not in tables:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('username', sa.Unicode(200)),
            sa.Column('country', sa.Unicode(200)),
            sa.Column('region', sa.Unicode(200)),
            sa.Column('timezone', sa.Unicode(25)),
            sa.Column('phone_number', sa.Unicode(15)),
            sa.Column('email', sa.Unicode(200)),
            sa.Column('preferences', sa.JSON),
        )

def downgrade():
    op.drop_table('stats')
    op.drop_table('deltas')
    op.drop_table('country_regions')
    op.drop_table('users')
