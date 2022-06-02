from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from config.db import Base

class Country(Base):
    __tablename__ = 'author_countries'
    id = Column(Integer, primary_key=True)
    name = Column('country_name', String(20))