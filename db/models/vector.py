from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, String, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class Vector(Base):
  __tablename__ = 'vector'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  name = Column(String)  
  threat_scenario_id = Column(UUID(as_uuid=True), ForeignKey('threat_scenario.id'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  threat_scenario = relationship('ThreatScenario', back_populates='vectors')

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }