"""create score table

Revision ID: 4bf4fb8d5edc
Revises: deb8284919bf
Create Date: 2022-06-16 15:11:50.216791

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '4bf4fb8d5edc'
down_revision = 'deb8284919bf'
branch_labels = None
depends_on = None


def upgrade() -> None:
  op.create_table(
    'score',
    sa.Column('id', UUID(as_uuid=True), primary_key=True, nullable=False),
    sa.Column('existence', sa.String()),
    sa.Column('maturity', sa.Integer()),
    sa.Column('effectiveness_relevance', sa.String()),
    sa.Column('effectiveness_timeliness', sa.String()),
    sa.Column('effectiveness_adaptability', sa.String()),
    sa.Column('group_coverage', sa.String()),
    sa.Column('company_id', UUID(as_uuid=True), sa.ForeignKey('company.id')),
    sa.Column('control_attribute_id', UUID(as_uuid=True), sa.ForeignKey('control_attribute.id')),
    sa.Column('control_assessment_id', UUID(as_uuid=True), sa.ForeignKey('control_assessment.id')),
    sa.Column('created_at', sa.DateTime()),
		sa.Column('updated_at', sa.DateTime())
  )

def downgrade() -> None:
  op.drop_table('score')