from alembic import command, config
from db.database import engine
from db.seed import seed_data
from src.lib.errors.errors_handler import exception_response
from src.lib.helpers.json_response import success

def upgrade_head(event, context):
  cfg = config.Config("alembic.ini")
  cfg.attributes['connection'] = engine  
  
  try:    
    command.upgrade(cfg, 'head')

    return success()
  except Exception as e:
    return exception_response(e)

def downgrade_base(event, context):  
  cfg = config.Config("alembic.ini")
  cfg.attributes['connection'] = engine
  
  try:
    command.downgrade(cfg, 'base')

    return success()
  except Exception as e:
    exception_response(e)

def data_migration(event, context):
  try:
    seed_data()

    return success()
  except Exception as e:
    exception_response(e)