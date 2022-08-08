"""create actor table

Revision ID: 47eb4ceb9ff1
Revises: 8755c92bf9b0
Create Date: 2022-06-16 12:01:59.293733

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '47eb4ceb9ff1'
down_revision = '8755c92bf9b0'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'actor',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String()),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('actor')