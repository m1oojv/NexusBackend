from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, DateTime, Boolean, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from db.models.base import Base
import uuid
import datetime

class ControlAttribute(Base):
  __tablename__ = 'control_attribute'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  control_id = Column(String)
  nist_function = Column(String)
  org_control_family = Column(String)
  description = Column(String)
  org_statement_type = Column(String)
  org_control_domain = Column(String)
  enterprise_bu = Column(String)
  maturity = Column(String)
  effectiveness_relevance = Column(String)
  effectiveness_timeliness = Column(String)
  effectiveness_adaptability = Column(String)
  coverage = Column(String)
  source_framework = Column(String)
  source_framework_code = Column(String)
  include_sme_assessment = Column(Boolean)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships  
  control_sme_estimated = relationship('ControlSmeEstimated', back_populates='control_attribute')
  scores = relationship('Score', back_populates='control_attribute')
  score_results = relationship('ScoreResult', back_populates='control_attribute')

  # Associations
  mitre_attack_techniques = association_proxy('mitre_attack_technique_control_attributes', 'mitre_attack_technique')
  threat_scenarios = association_proxy('threat_scenario_control_attributes', 'threat_scenario')

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }