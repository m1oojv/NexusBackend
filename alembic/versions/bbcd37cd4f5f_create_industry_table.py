"""create industry table

Revision ID: bbcd37cd4f5f
Revises: b0688ffd57b6
Create Date: 2022-06-16 12:10:48.075586

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'bbcd37cd4f5f'
down_revision = 'b0688ffd57b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'industry',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String()),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('industry')