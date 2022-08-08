from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, String, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class ControlSmeEstimated(Base):
  __tablename__ = 'control_sme_estimated'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  company_type = Column(String)
  scan_indicator = Column(String)  
  control_attribute_id = Column(UUID(as_uuid=True), ForeignKey('control_attribute.id'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  control_attribute = relationship('ControlAttribute', back_populates="control_sme_estimated")

  # Methods
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }