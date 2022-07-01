from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import Integer, Boolean, Date

from config.db import Base

from .book import Book
from .subscriber import Subscriber

class Loan(Base):
    __tablename__ = 'book_loans'
    id = Column(Integer, primary_key=True)
    loan_date = Column(Date)
    loan_exp_date = Column(Date)
    subscriber_id = Column(Integer, ForeignKey(Subscriber.id))
    book_id = Column(Integer, ForeignKey(Book))
    already_returned = Column(Boolean)
