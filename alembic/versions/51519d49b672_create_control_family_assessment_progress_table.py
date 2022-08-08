"""create control_family_assessment_progress table

Revision ID: 51519d49b672
Revises: 7af90c8ee2ab
Create Date: 2022-06-16 12:27:29.365353

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '51519d49b672'
down_revision = '7af90c8ee2ab'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'control_family_assessment_progress',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('control_family', sa.String()),
    sa.Column('assessment_progress', sa.String()),
    sa.Column('last_saved', sa.DateTime()),
    sa.Column('control_assessment_id', UUID(as_uuid=True), sa.ForeignKey('control_assessment.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('control_family_assessment_progress')