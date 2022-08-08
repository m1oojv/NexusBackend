from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Text, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from db.models.base import Base
import uuid
import datetime

class ThreatScenario(Base):
  __tablename__ = 'threat_scenario'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  title = Column(Text)
  description = Column(Text)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships  
  actors = relationship('Actor', back_populates='threat_scenario')
  vectors = relationship('Vector', back_populates='threat_scenario')
  industries = relationship('Industry', back_populates='threat_scenario')
  business_impacts = relationship('BusinessImpact', back_populates='threat_scenario')
  score_results = relationship('ScoreResult', back_populates='threat_scenario')

  # Asscociations
  mitre_attack_techniques = association_proxy('threat_scenario_mitre_attack_techniques', 'mitre_attack_technique')
  companies = association_proxy('company_threat_scenarios', 'company')
  control_attributes = association_proxy('threat_scenario_control_attributes', 'control_attribute')

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }