class BadRequest(Exception):
  
  def __init__(self, object={}, message='Bad Request', code=400):
    self.object = object
    self.message = message
    self.code = code
    
    super().__init__(self)