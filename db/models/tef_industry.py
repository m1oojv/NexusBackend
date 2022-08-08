from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Float, String, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class TefIndustry(Base):
  __tablename__ = 'tef_industry'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  industry = Column(String)
  threat_category= Column(String)
  risk = Column(String)
  ratio = Column(Float)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }