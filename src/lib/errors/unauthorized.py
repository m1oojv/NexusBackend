class Unauthorized(Exception):
  
  def __init__(self, object={}, message='Unauthorized', code=401):
    self.object = object
    self.message = message
    self.code = code
    
    super().__init__(self)