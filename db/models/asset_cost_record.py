from sqlalchemy import Column, String, Integer, Float, DateTime, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class AssetCostRecord(Base):
  __tablename__ = 'asset_cost_record'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  records_category = Column(Integer)
  cost_item = Column(String)
  cost_low = Column(Float)
  cost_mode = Column(Float)
  cost_high = Column(Float)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }