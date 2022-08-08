from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker

# engine = create_engine("postgresql://broker:pr0t0s123@development-nexus-db.ciosza4evk3o.ap-southeast-1.rds.amazonaws.com:5432/postgres", echo=True)
engine = create_engine("postgresql://postgres:postgres@localhost/nexus_broker_development")
if not database_exists(engine.url):
  create_database(engine.url)

# print(database_exists(engine.url))

Session = sessionmaker(engine)
session = Session(future=True)