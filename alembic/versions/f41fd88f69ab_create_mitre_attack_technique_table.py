"""create mitre_attack_technique table

Revision ID: f41fd88f69ab
Revises: 4bc37d0c7d26
Create Date: 2022-06-16 11:53:21.951924

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = 'f41fd88f69ab'
down_revision = '4bc37d0c7d26'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'mitre_attack_technique',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String()),
    sa.Column('technique_id', sa.String()),
    sa.Column('url', sa.String()),
    sa.Column('platforms', sa.String()),
    sa.Column('tactics', sa.String()),
    sa.Column('description', sa.String()),
    sa.Column('data_sources', sa.String()),
    sa.Column('detection', sa.String()),
    sa.Column('is_sub_technique', sa.Boolean()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )


def downgrade() -> None:
  op.drop_table('mitre_attack_technique')