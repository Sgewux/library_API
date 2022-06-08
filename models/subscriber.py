from sqlalchemy import Column, Enum
from sqlalchemy.types import Integer, String

from config.db import Base

class Subscriber(Base):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    second_name = Column(String(20))
    first_lastname = Column(String(20))
    second_lastname = Column(String(20))
    adress = Column(String(50))
    phone_number = Column(String(10))
    gender = Column(Enum('MALE', 'FEMALE'))
    status = Column(Enum('ACTIVE', 'INACTIVE'))