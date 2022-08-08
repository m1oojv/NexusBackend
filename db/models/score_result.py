from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, Float, String, Integer, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
from db.models.company import Company
import uuid
import datetime

class ScoreResult(Base):
  __tablename__ = 'score_result'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  existence = Column(String)
  maturity = Column(Integer)
  effectiveness_relevance = Column(String)
  effectiveness_timeliness = Column(String)
  effectiveness_adaptability = Column(String)
  group_coverage = Column(String)
  effectiveness_score = Column(Float)
  tri_score = Column(Float)
  tri_score_stage = Column(Float)
  nist_function = Column(String)
  company_id = Column(UUID(as_uuid=True), ForeignKey('company.id', ondelete='CASCADE'))
  control_attribute_id = Column(UUID(as_uuid=True), ForeignKey('control_attribute.id', ondelete='CASCADE'))
  threat_scenario_id = Column(UUID(as_uuid=True), ForeignKey('threat_scenario.id', ondelete='CASCADE'))
  control_assessment_id = Column(UUID(as_uuid=True), ForeignKey('control_assessment.id', ondelete='CASCADE'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  company = relationship(Company, back_populates='score_results')
  control_attribute = relationship('ControlAttribute', back_populates='score_results')
  threat_scenario = relationship('ThreatScenario', back_populates='score_results')

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }