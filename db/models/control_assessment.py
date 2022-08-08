from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, String, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class ControlAssessment(Base):
  __tablename__ = 'control_assessment'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  start_date = Column(DateTime, default= datetime.datetime.now)
  completed_datetime = Column(DateTime)
  last_saved = Column(DateTime)
  control_family_progress = Column(String)
  company_id = Column(UUID(as_uuid=True), ForeignKey('company.id', ondelete='CASCADE'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  company = relationship('Company', back_populates='control_assessments')
  scores = relationship('Score', back_populates='control_assessment', cascade='all, delete')
  control_family_assessment_progresses = relationship('ControlFamilyAssessmentProgress', back_populates='control_assessment', cascade='all, delete')

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }