from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, ForeignKey, DateTime, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class MitreAttackTechniqueControlAttribute(Base):
  __tablename__ = 'mitre_attack_technique_control_attribute'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  mitre_attack_technique_id = Column(UUID(as_uuid=True), ForeignKey('mitre_attack_technique.id'), primary_key=True)
  control_attribute_id = Column(UUID(as_uuid=True), ForeignKey('control_attribute.id'), primary_key=True)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  mitre_attack_technique = relationship('MitreAttackTechnique', backref=backref('mitre_attack_technique_control_attributes', cascade='all, delete-orphan'))
  control_attribute = relationship('ControlAttribute', backref=backref('mitre_attack_technique_control_attributes', cascade='all, delete-orphan'))

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }