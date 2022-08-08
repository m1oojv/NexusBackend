"""create control_assessment table

Revision ID: 7af90c8ee2ab
Revises: 3e17b9f13024
Create Date: 2022-06-16 12:24:30.868640

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '7af90c8ee2ab'
down_revision = '3e17b9f13024'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'control_assessment',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('start_date', sa.DateTime()),
    sa.Column('completed_datetime', sa.DateTime()),
    sa.Column('last_saved', sa.DateTime()),
    sa.Column('control_family_progress', sa.String()),
    sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('company.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )


def downgrade() -> None:
  op.drop_table('control_assessment')
