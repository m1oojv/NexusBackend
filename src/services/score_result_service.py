from sqlalchemy import select, update, delete, text
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import ScoreResult

import src.lib.helpers.helpers as helpers
from db.database import session

def create_record(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment_id = kwargs['control_assessment_id']
  body = kwargs['body']
  score_result = []
  for row in body:
    score_result.append(ScoreResult(
      company_id=row[0],
      control_attribute_id=row[1],
      existence=row[2],
      maturity=row[3],
      effectiveness_adaptability=row[4],
      effectiveness_relevance=row[5],
      effectiveness_timeliness=row[6],
      group_coverage=row[7],
      nist_function=row[8],
      threat_scenario_id=row[9],
      effectiveness_score=row[10],
      tri_score=row[11],
      tri_score_stage=row[12],
      control_assessment_id=control_assessment_id
    ))
  session.add_all(score_result)
  session.commit()
  score_result = find(company_id=company_id, control_assessment_id=control_assessment_id)

  return score_result

def find(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment_id = kwargs['control_assessment_id']
  score_result = select(ScoreResult).where((ScoreResult.company_id == company_id) & (ScoreResult.control_assessment_id == control_assessment_id))
  result = session.execute(score_result)

  return result.scalars().all()

def assess_company_score(score):
    object_list = []
    for row in score:
        effectiveness_score = 0
        maturity_score = float(row[3])
        if row[7] == "N/A":
            coverage = float(0)
        else:
            coverage = float(row[7])
        nist_stage = row[8]

        adaptability = convert_score(row[4], "adaptability")
        relevance = convert_score(row[5], "relevance")
        timeliness = convert_score(row[6], "timeliness")
        
        effectiveness_score = (relevance[0] + timeliness[0] + adaptability[0])/(relevance[1] + timeliness[1] + adaptability[1])
        
        tri_score = (maturity_score + (effectiveness_score * 2)) / 3 * coverage
        tri_score_stage = tri_stage(tri_score, nist_stage)
        row_list = list(row)
        row_list.append(effectiveness_score)
        row_list.append(tri_score)
        row_list.append(tri_score_stage)
        object_list.append(row_list)

    return object_list

def tri_stage(score, nist_stage):
    value = 0
    if nist_stage == "Identify":
        value = score * 0.2
    elif nist_stage == "Protect":
        value = score * 0.2
    elif nist_stage == "Detect":
        value = score * 0.20
    elif nist_stage == "Respond":
        value = score * 0.2
    elif nist_stage == "Recover":
        value = score * 0.2

    return value

def convert_score(score, metric):
    value = 0
    weight = 0

    if metric == "relevance":
        weight = 1
    elif metric == "timeliness":
        weight = 2
    elif metric == "adaptability":
        weight = 2

    if score == "N/A":
        value = 0
        weight = 0
    elif score == "Strong":
        value = 5 * weight
    elif score == "Moderate":
        value = 3 * weight
    elif score == "Weak":
        value = 1 * weight

    return value, weight
