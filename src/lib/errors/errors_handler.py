from src.lib.helpers.json_response import unauthorized, unprocessable_entity, bad_request, not_found, unknown_errors

def exception_response(error):
  class_name = error.__class__.__name__  

  if class_name == 'Unauthorized':    
    return unauthorized(error)
  elif class_name == 'BadRequest':
    return bad_request(error)
  elif class_name == 'NotFound':
    return not_found(error)
  elif class_name == 'UnprocessableEntity':
    return unprocessable_entity(error)

  return unknown_errors(error)