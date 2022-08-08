from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, DateTime, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class ThreatScenarioControlAttribute(Base):
  __tablename__ = 'threat_scenario_control_attribute'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  control_attribute_id = Column(UUID(as_uuid=True), ForeignKey('control_attribute.id'), primary_key=True)
  threat_scenario_id = Column(UUID(as_uuid=True), ForeignKey('threat_scenario.id'), primary_key=True)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  threat_scenario = relationship('ThreatScenario', backref=backref('threat_scenario_control_attributes', cascade='all, delete-orphan'))
  control_attribute = relationship('ControlAttribute', backref=backref('threat_scenario_control_attributes', cascade='all, delete-orphan'))

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }