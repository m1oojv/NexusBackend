from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, String, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models import control_assessment
from db.models.base import Base
import uuid
import datetime

class ControlFamilyAssessmentProgress(Base):
  __tablename__ = 'control_family_assessment_progress'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  control_family = Column(String)
  assessment_progress = Column(String)
  last_saved = Column(DateTime)  
  control_assessment_id = Column(UUID(as_uuid=True), ForeignKey('control_assessment.id', ondelete='CASCADE'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  control_assessment = relationship('ControlAssessment', back_populates='control_family_assessment_progresses')

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }