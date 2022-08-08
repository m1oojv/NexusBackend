class NotFound(Exception):
  
  def __init__(self, object={}, message='Not Found', code=404):
    self.object = object
    self.message = message
    self.code = code
    
    super().__init__(self)