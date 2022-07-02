from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import CheckViolation, ForeignKeyViolation
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from models.loan import Loan
from models.book import Book
from models.subscriber import Subscriber
from schemas.loan import LoanIn
from config.db import get_db_session

router = APIRouter(tags=['Loans'])

@router.post('/loans')
def add_loan(
    loan_info: LoanIn = Body(...),
    session: Session = Depends(get_db_session)
):
    already_borrowed = session.query(
        session.query(Loan).filter(
                Loan.book_id == loan_info.book_id, 
                Loan.already_returned == False
            ).exists()
        ).scalar()
    
    is_available = session.query(
        session.query(Book).filter(
            Book.id == loan_info.book_id,
            Book.available == True
        ).exists()
    ).scalar()

    condition = (is_available, not already_borrowed)

    if all(condition): # Book available AND not already burrowwed
        try:
            loan = Loan(
                loan_date=loan_info.loan_date,
                loan_exp_date=loan_info.loan_exp_date,
                subscriber_id=loan_info.subscriber_id,
                book_id=loan_info.book_id
            )
            session.add(loan)
            session.commit()
            session.refresh(loan)
        
        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig
            if type(postgres_error) == ForeignKeyViolation:
                raise HTTPException(
                    status_code=422,
                    detail=f'Subscriber id= {loan_info.subscriber_id} is not registered.'
                )

            elif type(postgres_error) == CheckViolation:
                raise HTTPException(
                    status_code=422,
                    detail='The max loan period is 1 month (loan_exp_date <= loan_date + 1 month)'
                )

    elif not condition[0]: # Book was NOT available
        raise HTTPException(
            status_code=422,
            detail=f'Book id= {loan_info.book_id} is not currently available in inventory or does not exist.'
        )

    elif not condition[1]: # Book was already borrowed
        raise HTTPException(
            status_code=422,
            detail=f'Book id= {loan_info.book_id} was borrowed and has not been returned yet'
        )
    