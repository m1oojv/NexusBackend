"""create company_threat_scenario table

Revision ID: 8755c92bf9b0
Revises: 00852340e7af
Create Date: 2022-06-16 12:00:12.053047

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '8755c92bf9b0'
down_revision = '00852340e7af'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'company_threat_scenario',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('company.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('company_threat_scenario')