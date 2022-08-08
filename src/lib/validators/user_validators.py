from src.lib.errors.unauthorized import Unauthorized
from src.lib.errors.not_found import NotFound
from src.lib.validators.common import is_valid_uuid

def valid_user(event):  
  if not event['requestContext']['authorizer']['jwt']:    
    raise Unauthorized()    

  if not is_valid_uuid(event['requestContext']['authorizer']['jwt']['claims']['sub']):
    raise Unauthorized()