from sqlalchemy import select, update, delete
from sqlalchemy.orm import joinedload, Load, lazyload, selectinload
from db.models import Industry
import src.lib.helpers.helpers as helpers
from db.database import session

def find(*args, **kwargs):
  if kwargs['select_all'] == True:
    industry = select(Industry).where((Industry.name == kwargs['industry']) | (Industry.name == 'All'))
  else:
    industry = select(Industry).where(Industry.name == kwargs['industry'])
  
  result = session.execute(industry)
  
  return result.scalars().all()  
