"""create asset_cost_fraud table

Revision ID: 741b085f1307
Revises: 95c9b0f64d6a
Create Date: 2022-06-16 15:22:24.162283

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '741b085f1307'
down_revision = '95c9b0f64d6a'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'asset_cost_fraud',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('company_size', sa.String()),
    sa.Column('cost', sa.Integer()),
    sa.Column('cost_item', sa.String()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('asset_cost_fraud')