"""Initial tables — users, farms, market_cache

Revision ID: 001
Revises:
Create Date: 2024-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('id',         sa.Integer(),  primary_key=True),
        sa.Column('email',      sa.String(),   nullable=False, unique=True),
        sa.Column('name',       sa.String(),   nullable=False),
        sa.Column('hashed_pw',  sa.String(),   nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'farms',
        sa.Column('id',            sa.Integer(), primary_key=True),
        sa.Column('name',          sa.String(),  nullable=False),
        sa.Column('owner_id',      sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('lat',           sa.Float(),   nullable=False),
        sa.Column('lng',           sa.Float(),   nullable=False),
        sa.Column('location_name', sa.String(),  nullable=True),
        sa.Column('soil_type',     sa.String(),  nullable=True),
        sa.Column('soil_ph',       sa.Float(),   nullable=True),
        sa.Column('land_area',     sa.Float(),   nullable=True),
        sa.Column('season',        sa.String(),  nullable=True),
        sa.Column('saved_crops',   sa.JSON(),    nullable=True),
        sa.Column('created_at',    sa.DateTime(),nullable=True),
        sa.Column('updated_at',    sa.DateTime(),nullable=True),
    )
    op.create_table(
        'market_cache',
        sa.Column('id',         sa.Integer(), primary_key=True),
        sa.Column('crop_name',  sa.String(),  nullable=False, unique=True),
        sa.Column('price',      sa.Float(),   nullable=True),
        sa.Column('unit',       sa.String(),  nullable=True),
        sa.Column('source',     sa.String(),  nullable=True),
        sa.Column('fetched_at', sa.DateTime(),nullable=True),
    )

def downgrade():
    op.drop_table('market_cache')
    op.drop_table('farms')
    op.drop_table('users')
