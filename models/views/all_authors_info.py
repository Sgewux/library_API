from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Enum

from config.db import Base

class AllAuthorsInfo(Base):
    '''
    SQL view that represents a join between:
        - Authors
        - Author_countries
    gives us a nice representation of all the 
    necessary data that can be extracted from an author
    '''

    __tablename__ = 'all_authors_info'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(20))
    second_name = Column(String(20))
    first_lastname = Column(String(20))
    second_lastname = Column(String(20))
    gender = Column(Enum('MALE', 'FEMALE'))
    country = Column(String(20))