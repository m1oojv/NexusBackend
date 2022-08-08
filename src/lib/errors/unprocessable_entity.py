class UnprocessableEntity(Exception):
  
  def __init__(self, object={}, message='Unprocessable Entity', code=422):
    self.object = object
    self.message = message
    self.code = code
    
    super().__init__(self)