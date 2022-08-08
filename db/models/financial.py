from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey, DateTime, Float, String, Integer, inspect
from sqlalchemy.dialects.postgresql import UUID, JSONB
from db.models.base import Base
import uuid
import datetime

class Financial(Base):
  __tablename__ = 'financial'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  risk = Column(Float)  
  premium = Column(Float)
  limits = Column(Float)  
  loss_exceedence = Column(JSONB)
  threat_category_losses = Column(JSONB)
  claims = Column(Float)
  loss_by_return_period = Column(JSONB)  
  company_id = Column(UUID(as_uuid=True), ForeignKey('company.id', ondelete='CASCADE'))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  company = relationship('Company', back_populates="financial")

  # Methods
  def __repr__(self):
    return f"Financial(id={self.id!r}, risk={self.risk!r}"

  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }