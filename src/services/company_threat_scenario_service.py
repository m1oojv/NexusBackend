from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import CompanyThreatScenario
import src.lib.helpers.helpers as helpers
from db.database import session

def create_all(*args, **kwargs):
  company_threat_scenario = []
  for r in kwargs['company_threat_scenario']:
    company_threat_scenario.append(CompanyThreatScenario(
      company_id = r['company_id'], 
      threat_scenario_id = r['threat_scenario_id']
    ))
  
  session.add_all(company_threat_scenario)
  session.commit()
  
  return  

def create_sme(*args, **kwargs):
  company_id = kwargs['company_id']
  company_threat_scenario = []
  
  for r in kwargs['threat_scenarios']:
    company_threat_scenario.append({
      'company_id': company_id, 
      'threat_scenario_id': r['threat_scenario_id'], 
      })
  return create_all(company_threat_scenario=company_threat_scenario)