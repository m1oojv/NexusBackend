"""create tef_industry table

Revision ID: 83fdd8ffd8af
Revises: 9f27acc70af8
Create Date: 2022-06-16 15:37:01.307342

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '83fdd8ffd8af'
down_revision = '9f27acc70af8'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'tef_industry',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('industry', sa.String()),
    sa.Column('threat_category', sa.String()),
    sa.Column('risk', sa.String()),
    sa.Column('ratio', sa.Float()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('tef_industry')