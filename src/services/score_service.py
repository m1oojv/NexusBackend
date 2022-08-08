from sqlalchemy import select, update, delete, text
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import Score, ControlSmeEstimated, ControlFamilyAssessmentProgress, ControlAssessment

import src.lib.helpers.helpers as helpers
from db.database import session

def all(*args, **kwargs):
  company_id = kwargs['company_id']
  score = select(Score).where(Score.company_id == company_id)
  result = session.execute(score)
  
  return result.scalars().all()

def find(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment_id = kwargs['control_assessment_id']
  score = select(Score).where((Score.company_id == company_id) & (Score.control_assessment_id == control_assessment_id))
  result = session.execute(score)
  
  return result.scalars().all()

def create(*args, **kwargs):
  score = Score(**kwargs)
  
  session.add(score)
  session.commit()
  session.refresh(score)

  return score

def create_all(*args, **kwargs):
  score = []
  for r in kwargs['score']:
    score.append(Score(
      control_attribute_id = r['control_attribute_id'], 
      control_assessment_id = r['control_assessment_id'], 
      company_id = r['company_id'], 
      existence = r['existence']
    ))
  
  session.add_all(score)
  session.commit()
  score = find(company_id=kwargs['company_id'], control_assessment_id=kwargs['control_assessment_id'])
  return score

def create_sme_control(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment = kwargs['control_assessment']

  #retrieve SME controls
  sme_controls = select(ControlSmeEstimated)
  result = session.execute(sme_controls).scalars().all()

  score = []
  for control in result:
    control_score = {
      'control_attribute_id': control.control_attribute_id, 
      'control_assessment_id': control_assessment.id, 
      'company_id': company_id, 
      'existence': 'Exists'
      }
    score.append(control_score)

  return create_all(score=score, company_id=company_id, control_assessment_id=control_assessment.id)

def update_many_record(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment_id = kwargs['control_assessment_id']
  body = kwargs['body']
  for row in body:
    query = update(Score).where((Score.control_assessment_id == control_assessment_id) & (Score.control_attribute_id == row['control_attribute_id'])).values(row['body']).execution_options(synchronize_session="fetch")
    session.execute(query)
  
  session.commit()

  score = find(company_id=company_id, control_assessment_id=control_assessment_id)
  return score

def get_score_result_params(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment_id = kwargs['control_assessment_id']
  query = """
        select score.company_id, score.control_attribute_id, score.existence, score.maturity, score.effectiveness_adaptability, score.effectiveness_relevance, \
        score.effectiveness_timeliness, score.group_coverage, ca.nist_function, a.threat_scenario_id FROM company_threat_scenario as a \
        inner join threat_scenario_control_attribute as c on a.threat_scenario_id = c.threat_scenario_id \
        inner join score as score on a.company_id = score.company_id and c.control_attribute_id = score.control_attribute_id \
        inner join control_attribute as ca on score.control_attribute_id = ca.id \
        where score.company_id  = :company_id and score.control_assessment_id =:control_assessment_id
        """
  result = session.execute(text(query), {'company_id': company_id, 'control_assessment_id': control_assessment_id}).all()
  return result
  