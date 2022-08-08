from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class Score(Base):
  __tablename__ = 'score'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  existence = Column(String)
  maturity = Column(Integer)
  effectiveness_relevance = Column(String)
  effectiveness_timeliness = Column(String)
  effectiveness_adaptability = Column(String)
  group_coverage = Column(String)
  company_id = Column(UUID(as_uuid=True), ForeignKey('company.id', ondelete='CASCADE'))
  control_attribute_id = Column(UUID(as_uuid=True), ForeignKey('control_attribute.id'))
  control_assessment_id = Column(UUID(as_uuid=True), ForeignKey('control_assessment.id', ondelete='CASCADE'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  company = relationship('Company', back_populates='scores')
  control_attribute = relationship('ControlAttribute', back_populates='scores')
  control_assessment = relationship('ControlAssessment', back_populates='scores')

  # Methods
  def __repr__(self):
    return f"Score(id={self.id!r}, existence={self.existence!r}"
  
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }