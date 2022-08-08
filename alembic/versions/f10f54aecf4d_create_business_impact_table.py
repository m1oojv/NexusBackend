"""create business_impact table

Revision ID: f10f54aecf4d
Revises: bbcd37cd4f5f
Create Date: 2022-06-16 12:11:46.346146

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'f10f54aecf4d'
down_revision = 'bbcd37cd4f5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'business_impact',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String()),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('business_impact')