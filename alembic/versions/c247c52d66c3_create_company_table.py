"""create company table

Revision ID: c247c52d66c3
Revises: 
Create Date: 2022-06-16 11:49:11.111055

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = 'c247c52d66c3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'company',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('name', sa.String()),
    sa.Column('revenue', sa.Float()),
    sa.Column('industry', sa.String()),
    sa.Column('country', sa.String()),
    sa.Column('description', sa.String()),
    sa.Column('assessment_progress', sa.String()),
    sa.Column('last_assessed_at', sa.DateTime()),
    sa.Column('employees', sa.Integer()),
    sa.Column('domain', sa.String()),
    sa.Column('threat_assessment_status', sa.String()),
    sa.Column('scan_status', sa.String()),
    sa.Column('pii', sa.Integer()),
    sa.Column('pci', sa.Integer()),
    sa.Column('phi', sa.Integer()),
    sa.Column('control_status', sa.String()),
    sa.Column('scan_results', JSONB()),
    sa.Column('estimated_controls', sa.String()),
    sa.Column('application_datetime', sa.DateTime()),
    sa.Column('tenant_id', UUID(as_uuid=True)),
    sa.Column('user_id', UUID(as_uuid=True)),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )


def downgrade() -> None:
  op.drop_table('company')