from sqlalchemy.orm import relationship
from sqlalchemy import event, Column, Float, Integer, DateTime, String, inspect, null
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.associationproxy import association_proxy
from db.models.base import Base
import uuid
import datetime

class Company(Base):
  __tablename__ = 'company'

  # Fields
  id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4())
  name = Column(String)
  revenue = Column(Float)
  industry = Column(String)
  country = Column(String)
  description = Column(String)
  assessment_progress = Column(String)
  last_assessed_at = Column(DateTime)
  employees = Column(Integer)
  domain = Column(String)
  threat_assessment_status = Column(String)
  scan_status = Column(String)
  pii = Column(Integer)
  pci = Column(Integer)
  phi = Column(Integer)
  control_status = Column(String)
  scan_results = Column(JSONB)
  estimated_controls = Column(String)
  application_datetime = Column(DateTime, default= datetime.datetime.now)
  tenant_id = Column(UUID(as_uuid=True))
  user_id = Column(UUID(as_uuid=True))
  created_at = Column(DateTime, default= datetime.datetime.now)
  updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

  # Relationships
  financial = relationship('Financial', back_populates='company', uselist=False, cascade='all, delete')
  control_assessments = relationship('ControlAssessment', back_populates='company', cascade='all, delete')  
  scores = relationship('Score', back_populates='company', cascade='all, delete')
  score_results = relationship('ScoreResult', back_populates='company', cascade='all, delete')

  # Associations
  threat_scenarios = association_proxy('company_threat_scenarios', 'threat_scenario')

  # Methods
  def __repr__(self):    
    return f"Company(id={self.id!r}, name={self.name!r})"
  
  def to_dict(self):
    return { c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs }


# Listeners
def before_insert_listener(mapper, connection, target):  
  if target.last_assessed_at == '':
    target.last_assessed_at = null()

  if target.application_datetime == '':
    target.application_datetime = null()

  # For testing now
  if target.tenant_id == '':
    target.tenant_id = null()

  if target.user_id == '':
    target.user_id = null()
# Events  
event.listen(Company, "before_insert", before_insert_listener)