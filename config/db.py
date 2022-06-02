import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

engine = create_engine(
    f'postgresql+psycopg2://postgres:{os.getenv("DBPASSWD")}@localhost:5432/library'
)


Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
