from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String, Enum

from config.db import Base
from .country import Country

class Author(Base):
    __tablename__ = 'authors'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    second_name = Column(String(20))
    first_lastname = Column(String(20))
    second_lastname = Column(String(20))
    gender = Column(Enum('MALE', 'FEMALE'))
    country_id = Column(Integer, ForeignKey(Country.id))