from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from models.loan import Loan
from models.book import Book
from schemas.loan import LoanIn
from config.db import get_db_session

router = APIRouter(tags=['Loans'])

@router.post('/loans')
def add_loan(
    loan_info: LoanIn = Body(...),
    session: Session = Depends(get_db_session)
):
    already_burrowed = session.query(
        session.query(Loan).filter(
                Loan.book_id == loan_info.book_id, 
                Loan.already_returned == False
            ).exists()
        ).scalar()
    
    is_available = session.query(
        session.query(Book).filter(
            Book.id == loan_info.book_id,
            Book.available == True
        )
    )

    condition = (is_available, not already_burrowed)

    if all(condition): # Book available AND not already burrowwed
        pass
    elif not condition[0]: # Book was NOT available
        pass
    elif not condition[1]: # Book was already burrowd
        pass
    