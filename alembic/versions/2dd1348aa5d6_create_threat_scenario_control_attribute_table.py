"""create threat_scenario_control_attribute table

Revision ID: 2dd1348aa5d6
Revises: f10f54aecf4d
Create Date: 2022-06-16 12:13:16.343871

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '2dd1348aa5d6'
down_revision = 'f10f54aecf4d'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'threat_scenario_control_attribute',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('control_attribute_id', UUID(as_uuid=True), sa.ForeignKey('control_attribute.id')),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('threat_scenario_control_attribute')