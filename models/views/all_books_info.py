from sqlalchemy import Column
from sqlalchemy.types import Integer, String, Enum

from config.db import Base

class AllBooksInfo(Base):
    '''
    SQL View that represents a join betwen:
        - Books
        - Authors
        - Categories
        - Authors_countries

    gives us a very nice representation of all the
    necessary data that can be extracted from a book
    '''
    __tablename__ = 'all_books_info'

    id = Column(Integer, primary_key=True)
    book_name = Column(String(20))
    category = Column(String(20))
    author_id = Column(Integer)
    author_first_name = Column(String(20))
    author_second_name = Column(String(20))
    author_first_lastname = Column(String(20))
    author_second_lastname = Column(String(20))
    author_gender = Column(Enum('MALE', 'FEMALE'))
    author_country = Column(String(20))
    floor = Column(Integer)
    shelf_number = Column(Integer)
    shelf_row_num = Column(Integer)
