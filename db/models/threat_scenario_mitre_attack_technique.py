from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, DateTime, String, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class ThreatScenarioMitreAttackTechnique(Base):
  __tablename__ = 'threat_scenario_mitre_attack_technique'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  killchain_stage = Column(String)
  threat_scenario_id = Column(UUID(as_uuid=True), ForeignKey('threat_scenario.id'), primary_key=True)
  mitre_attack_technique_id = Column(UUID(as_uuid=True), ForeignKey('mitre_attack_technique.id'), primary_key=True)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
  
  # Relationships
  threat_scenario = relationship('ThreatScenario', backref=backref('threat_scenario_mitre_attack_techniques', cascade='all, delete-orphan'))
  mitre_attack_technique = relationship('MitreAttackTechnique', backref=backref('threat_scenario_mitre_attack_techniques', cascade='all, delete-orphan'))

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }