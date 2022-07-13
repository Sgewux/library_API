from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Enum, Text

from config.db import Base

class Librarian(Base):
    __tablename__ = 'librarians'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    second_name = Column(String(20))
    first_lastname = Column(String(20))
    second_lastname = Column(String(20))
    role = Column(Enum('SUPERVISOR', 'VOLUNTEER'))
    access_password = Column(Text())