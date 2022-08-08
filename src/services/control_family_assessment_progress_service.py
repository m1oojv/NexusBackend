from sqlalchemy import select, update, delete, text
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import Score, ControlFamilyAssessmentProgress, ControlAssessment, control_family_assessement_progress

import src.lib.helpers.helpers as helpers
from db.database import session

def create_sme_control(*args, **kwargs):
  company_id = kwargs['company_id']
  control_assessment = kwargs['control_assessment']
  #retrieve control families
  control_families = """select distinct ca.org_control_family FROM score svs inner join control_attribute ca on svs.control_attribute_id = ca.id \
              cross join control_assessment as assess where assess.id = :control_assessment_id order by ca.org_control_family asc
              """
  control_family_assessement_progress = []
  for control_family in session.execute(text(control_families), {'control_assessment_id': control_assessment.id}).scalars().all():
    control_family_assessement_progress.append({
      'control_assessment_id': control_assessment.id, 
      'control_family': control_family, 
      'assessment_progress': 'COMPLETED'
      })

  return create_all(params=control_family_assessement_progress)

def create_all(*args, **kwargs):
  control_family_assessement_progress = []
  for r in kwargs['params']:
    control_family_assessement_progress.append(ControlFamilyAssessmentProgress(
      control_assessment_id = r['control_assessment_id'], control_family = r['control_family'], assessment_progress = r['assessment_progress'])
    )
  session.add_all(control_family_assessement_progress)
  session.commit()

  return kwargs['params']