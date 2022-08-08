"""create vector table

Revision ID: 7886a2eeef3d
Revises: 47eb4ceb9ff1
Create Date: 2022-06-16 12:03:16.147884

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '7886a2eeef3d'
down_revision = '47eb4ceb9ff1'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'vector',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String()),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('vector')