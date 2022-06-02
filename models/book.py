from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, String

from config.db import Base

from .author import Author
from .category import Category

class Book(Base):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    book_name = Column(String(20))
    shelf_row_num = Column(Integer)
    category_id = Column(Integer, ForeignKey(Author.id))
    author_id = Column(Integer, ForeignKey(Category.id))