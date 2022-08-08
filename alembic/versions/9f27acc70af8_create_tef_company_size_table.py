"""create tef_company_size table

Revision ID: 9f27acc70af8
Revises: aed83e3d8644
Create Date: 2022-06-16 15:33:15.470124

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '9f27acc70af8'
down_revision = 'aed83e3d8644'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'tef_company_size',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('threat_category', sa.String()),
    sa.Column('company_size', sa.String()),
    sa.Column('tef_low', sa.Float()),
    sa.Column('tef_mode', sa.Float()),
    sa.Column('tef_high', sa.Float()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('tef_company_size')