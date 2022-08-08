from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
import os

username = os.environ["DB_USER"]
password = os.environ["DB_PASS"]
host = os.environ["DB_HOST"]
port = os.environ["DB_PORT"]
dbname = os.environ["DB_NAME"]

engine = create_engine(f"postgresql://{username}:{password}@{host}:{port}/{dbname}")

if not database_exists(engine.url):
  create_database(engine.url)

Session = sessionmaker(engine)
session = Session(future=True)