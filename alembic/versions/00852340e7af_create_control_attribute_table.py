"""create control_attribute table

Revision ID: 00852340e7af
Revises: f41fd88f69ab
Create Date: 2022-06-16 11:56:58.104080

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '00852340e7af'
down_revision = 'f41fd88f69ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'control_attribute',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('control_id', sa.String()),
    sa.Column('nist_function', sa.String()),
    sa.Column('org_control_family', sa.String()),
    sa.Column('description', sa.String()),
    sa.Column('org_statement_type', sa.String()),
    sa.Column('org_control_domain', sa.String()),
    sa.Column('enterprise_bu', sa.String()),
    sa.Column('maturity', sa.String()),
    sa.Column('effectiveness_relevance', sa.String()),
    sa.Column('effectiveness_timeliness', sa.String()),
    sa.Column('effectiveness_adaptability', sa.String()),
    sa.Column('coverage', sa.String()),
    sa.Column('source_framework', sa.String()),
    sa.Column('source_framework_code', sa.String()),
    sa.Column('include_sme_assessment', sa.Boolean()),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )


def downgrade() -> None:
  op.drop_table('control_attribute')