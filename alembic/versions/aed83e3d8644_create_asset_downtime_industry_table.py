"""create asset_downtime_industry table

Revision ID: aed83e3d8644
Revises: 292588c76554
Create Date: 2022-06-16 15:30:11.843350

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = 'aed83e3d8644'
down_revision = '292588c76554'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'asset_downtime_industry',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('industry', sa.String()),
    sa.Column('threat_category', sa.String()),
    sa.Column('impact', sa.String()),
    sa.Column('ratio', sa.Float()),
    sa.Column('downtime_low', sa.Integer()),
    sa.Column('downtime_mode', sa.Integer()),
    sa.Column('downtime_high', sa.Integer()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('asset_downtime_industry')