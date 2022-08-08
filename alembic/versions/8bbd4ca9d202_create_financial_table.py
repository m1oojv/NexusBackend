"""create financial table

Revision ID: 8bbd4ca9d202
Revises: c247c52d66c3
Create Date: 2022-06-16 11:50:26.824619

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '8bbd4ca9d202'
down_revision = 'c247c52d66c3'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'financial',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('risk', sa.Float()),
    sa.Column('premium', sa.Float()),
    sa.Column('limits', sa.Float()),
    sa.Column('loss_exceedence', JSONB()),
    sa.Column('threat_category_losses', JSONB()),
    sa.Column('claims', sa.Float()),
    sa.Column('loss_by_return_period', JSONB()),
    sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('company.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )


def downgrade() -> None:
  op.drop_table('financial')