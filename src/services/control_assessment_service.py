from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import ControlAssessment
import src.lib.helpers.helpers as helpers
from db.database import session

def all(params):
  company_id = params['company_id']
  
  control_assessment = select(ControlAssessment).where(ControlAssessment.company_id == company_id)
  result = session.execute(control_assessment)
  
  return result.scalars().all()  

def create(params):
  control_assessment = ControlAssessment(**params)
  
  session.add(control_assessment)
  session.commit()
  session.refresh(control_assessment)

  return control_assessment

def delete_record(id):  
  control_assessment = session.query(ControlAssessment).filter_by(id=id).first()

  session.delete(control_assessment)
  session.commit()