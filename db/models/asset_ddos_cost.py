from sqlalchemy import Column, String, Integer, DateTime, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class AssetDdosCost(Base):
  __tablename__ = 'asset_ddos_cost'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  company_size = Column(String)
  cost = Column(Integer)  
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }