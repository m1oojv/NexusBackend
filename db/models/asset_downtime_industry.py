from sqlalchemy import Column, String, Integer, Float, DateTime, inspect
from sqlalchemy.dialects.postgresql import UUID
from db.models.base import Base
import uuid
import datetime

class AssetDowntimeIndustry(Base):
  __tablename__ = 'asset_downtime_industry'

  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  industry = Column(String)
  threat_category = Column(String)
  impact = Column(String)
  ratio = Column(Float)
  downtime_low = Column(Integer)
  downtime_mode = Column(Integer)
  downtime_high = Column(Integer)
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }