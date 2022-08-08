"""create threat_scenario table

Revision ID: 4bc37d0c7d26
Revises: 8bbd4ca9d202
Create Date: 2022-06-16 11:51:56.797914

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '4bc37d0c7d26'
down_revision = '8bbd4ca9d202'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'threat_scenario',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('title', sa.Text()),
    sa.Column('description', sa.Text()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('threat_scenario')