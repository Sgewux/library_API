import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

load_dotenv()

engine = create_engine(
    f'postgresql+psycopg2://postgres:{os.getenv("DBPASSWD")}@localhost:5432/library'
)


Base = declarative_base()
session_factory = sessionmaker(autocommit=False, bind=engine)

def get_db_session() -> Session:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()