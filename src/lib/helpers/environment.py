import os

def development_environment():
  return os.environ['STAGE'] == 'dev'

def staging_environment():
  return os.environ['STAGE'] == 'staging'