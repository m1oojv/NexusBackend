"""create threat_scenario_mitre_attack_technique table

Revision ID: b0688ffd57b6
Revises: 7886a2eeef3d
Create Date: 2022-06-16 12:07:51.801929

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'b0688ffd57b6'
down_revision = '7886a2eeef3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'threat_scenario_mitre_attack_technique',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('killchain_stage', sa.String()),
    sa.Column('mitre_attack_technique_id', UUID(as_uuid=True), sa.ForeignKey('mitre_attack_technique.id')),
    sa.Column('threat_scenario_id', UUID(as_uuid=True), sa.ForeignKey('threat_scenario.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('threat_scenario_mitre_attack_technique')
