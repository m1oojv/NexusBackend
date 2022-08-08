from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import Company, Financial
import src.lib.helpers.helpers as helpers
from db.database import session

def all(**kwargs):
  user_id = kwargs['user_id']
  
  company = select(Company).where(Company.user_id == user_id)
  result = session.execute(company)
  
  return result.scalars().all()  

def create(**kwargs):
  company = Company(**kwargs)
  print(company)
  session.add(company)
  session.commit()
  session.refresh(company)

  financial = Financial(company_id=company.id)
  session.add(financial)
  session.commit()

  return company

def find(**kwargs):
  id = kwargs['id']
  user_id = kwargs['user_id']
  if kwargs['joinedload'] == True:
    company = select(Company).options(joinedload(Company.financial, innerjoin=True)).options(joinedload(Company.control_assessments, innerjoin=True)).where((Company.id == id) & (Company.user_id == user_id))
    result = session.execute(company).scalars().first()

    #parse result object to dict
    result = result.__dict__
    result['financial'] = result['financial'].__dict__

    control_assessments_dict = []
    for row in result['control_assessments']:
      control_assessments_dict.append(row.__dict__)

    result['control_assessments'] = control_assessments_dict

    #format scan results
    result['scan_results']['data'] = helpers.filter_scan_info(result['scan_results']['data'])
    result['scan_results']['risk_recommendations'] = helpers.filter_rec_info(result['scan_results']['risk_recommendations'])
  else:
    company = select(Company).where((Company.id == id) & (Company.user_id == user_id))
    result = session.execute(company).scalars().first()

  return result

def update_record(**kwargs):
  id = kwargs['id']
  body = kwargs['body']
  user_id = kwargs['user_id']
  query = update(Company).where(Company.id == id).values(body).execution_options(synchronize_session="fetch")
  session.execute(query)
  session.commit()
  
  company = find(id=id, user_id=user_id, joinedload=False)
  
  return company

def delete_record(**kwargs):  
  company = session.query(Company).filter_by(id=kwargs['id'], user_id=kwargs['user_id']).first()

  session.delete(company)
  session.commit()