"""create asset_ddos_cost table

Revision ID: 292588c76554
Revises: 953686cc57af
Create Date: 2022-06-16 15:27:33.889832

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '292588c76554'
down_revision = '953686cc57af'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'asset_ddos_cost',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('company_size', sa.String()),
    sa.Column('cost', sa.Integer()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('asset_ddos_cost')