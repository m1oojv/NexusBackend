from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import ControlSmeEstimated
import src.lib.helpers.helpers as helpers
from db.database import session

def all():
  control_sme_estimated = select(ControlSmeEstimated)
  result = session.execute(control_sme_estimated)
  
  return result.scalars().all()