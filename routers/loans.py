from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import CheckViolation, ForeignKeyViolation
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Path, Body, HTTPException, Depends, Response

from models.loan import Loan
from models.book import Book
from config.db import get_db_session
from models.subscriber import Subscriber
from schemas.enums import SubscriberStatus
from schemas.loan import LoanIn, LoanOut
from utils.auth import get_librarian_session

router = APIRouter(tags=['Loans'])

@router.post('/loans', response_class=RedirectResponse)
def add_loan(
    loan_info: LoanIn = Body(...),
    session: Session = Depends(get_db_session),
    _ = Depends(get_librarian_session)  # A librarian must be authenticated, no matter the role
):
    already_borrowed = session.query(
        session.query(Loan).filter(
                Loan.book_id == loan_info.book_id, 
                Loan.already_returned == False
            ).exists() # Converts query into exists query EXISTS(SELECT ....)
        ).scalar() # Returns first value of first row (in this case we'll see only one val and one row cause is a SELECT EXISTS(...))
    
    is_available = session.query(
        session.query(Book).filter(
            Book.id == loan_info.book_id,
            Book.available == True
        ).exists()
    ).scalar()

    is_active_sub = session.query(
        session.query(Subscriber).filter(
            Subscriber.id == loan_info.subscriber_id,
            Subscriber.status == SubscriberStatus.ACTIVE.value
        ).exists()
    ).scalar()

    condition = (is_available, not already_borrowed, is_active_sub)

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

            return RedirectResponse(f'/loans/{loan.id}', status_code=303)
        
        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig

            if type(postgres_error) == CheckViolation:
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
    
    elif not condition[2]: # Book not registered or not active
        raise HTTPException(
            status_code=422,
            detail=f'Subscriber id= {loan_info.subscriber_id} is not registered or is not active.'
        )


@router.get('/loans/{loan_id}', response_model=LoanOut)
def get_loan(
    loan_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session),
    _ = Depends(get_librarian_session)
):
    result = session.get(Loan, loan_id)
    if result is not None:
        return LoanOut.build_instance_from_orm(result)
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent loan id= {loan_id}'
        )


@router.delete(
    '/loans/{loan_id}', 
    status_code=204,
    response_class=Response
    )
def mark_loan_as_returned(
    loan_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session),
    _ = Depends(get_librarian_session)
):
    loan = session.get(Loan, loan_id)
    if loan is not None:
        session.delete(loan)
        session.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not mark as returned unexistent loan id= {loan_id}'
        )