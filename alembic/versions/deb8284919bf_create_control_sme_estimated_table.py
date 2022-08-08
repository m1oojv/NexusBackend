"""create control_sme_estimated table

Revision ID: deb8284919bf
Revises: 51519d49b672
Create Date: 2022-06-16 14:04:36.353944

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'deb8284919bf'
down_revision = '51519d49b672'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'control_sme_estimated',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('company_type', sa.String()),
    sa.Column('scan_indicator', sa.String()),
    sa.Column('control_attribute_id', UUID(as_uuid=True), sa.ForeignKey('control_attribute.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('control_sme_estimated')