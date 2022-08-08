"""create asset_cost_record table

Revision ID: 953686cc57af
Revises: 741b085f1307
Create Date: 2022-06-16 15:24:23.424587

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '953686cc57af'
down_revision = '741b085f1307'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'asset_cost_record',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('records_category', sa.Integer()),
    sa.Column('cost_item', sa.String()),
    sa.Column('cost_low', sa.Float()),
    sa.Column('cost_mode', sa.Float()),
    sa.Column('cost_high', sa.Float()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('asset_cost_record')