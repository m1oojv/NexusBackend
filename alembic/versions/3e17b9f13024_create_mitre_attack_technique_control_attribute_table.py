"""create mitre_attack_technique_control_attribute table

Revision ID: 3e17b9f13024
Revises: 2dd1348aa5d6
Create Date: 2022-06-16 12:19:50.861224

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '3e17b9f13024'
down_revision = '2dd1348aa5d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'mitre_attack_technique_control_attribute',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('mitre_attack_technique_id', UUID(as_uuid=True), sa.ForeignKey('mitre_attack_technique.id')),
    sa.Column('control_attribute_id', UUID(as_uuid=True), sa.ForeignKey('control_attribute.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('mitre_attack_technique_control_attribute')