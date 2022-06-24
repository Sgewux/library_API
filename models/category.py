from sqlalchemy import Column
from sqlalchemy.types import Integer, String

from config.db import Base

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    category_name = Column(String(20))
    floor = Column(Integer)
    shelf_number = Column(Integer)