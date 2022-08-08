from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, Boolean, inspect
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.associationproxy import association_proxy
from db.models.base import Base
import uuid
import datetime

class MitreAttackTechnique(Base):
  __tablename__ = 'mitre_attack_technique'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  name = Column(String)
  technique_id = Column(String)
  url = Column(String)
  platforms = Column(String)
  tactics = Column(String)
  description = Column(String)
  data_sources = Column(String)
  detection = Column(String)
  is_sub_technique = Column(Boolean)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships

  # Associations
  control_attributes = association_proxy('mitre_attack_technique_control_attributes', 'control_attribute')
  threat_scenarios = association_proxy('threat_scenario_mitre_attack_techniques', 'threat_scenario')
  
  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }