from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, InternalError
from psycopg2.errors import UniqueViolation, RaiseException
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from config.db import get_db_session
from models.loan import Loan
from models.subscriber import Subscriber
from schemas.loan import LoanOut
from utils.auth import get_librarian_session
from schemas.subscriber import SubscriberIn, SubscriberOut, SubscriberUpdate

router = APIRouter(tags=['Subscribers'])

@router.post('/subscribers', response_class=RedirectResponse)
def add_subscriber(
    new_subscriber: SubscriberIn = Body(...),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    subscriber = Subscriber(
        id = new_subscriber.id,
        first_name = new_subscriber.first_name,
        second_name = new_subscriber.second_name,
        first_lastname = new_subscriber.first_lastname,
        second_lastname = new_subscriber.second_lastname,
        adress = new_subscriber.adress,
        phone_number = new_subscriber.phone_number,
        gender = new_subscriber.gender.value
    )

    try:
        session.add(subscriber)
        session.commit()
        session.refresh(subscriber)

        return RedirectResponse(f'/subscribers/{subscriber.id}', status_code=303)
    
    except IntegrityError as e:
        session.rollback()
        postgres_error = e.orig

        if type(postgres_error) == UniqueViolation:
            raise HTTPException(
                status_code=422,
                detail=f'Phone number {subscriber.phone_number} is an already used phone number'
            )

    except InternalError as e:
        session.rollback()
        postgres_error = e.orig

        raise HTTPException(
            status_code=422,
            detail=str(postgres_error).split('\n')[0]
        )


@router.get('/subscribers', response_model=List[SubscriberOut])
def get_subscribers(
    only_active: bool = Query(True),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    q = session.query(Subscriber)
    if only_active:
        q = q.filter(Subscriber.status == 'ACTIVE')
    
    results = q.all()
        
    return list(map(SubscriberOut.build_instance_from_orm, results))


@router.get('/subscribers/{subscriber_id}', response_model=SubscriberOut)
def get_subscriber(
    subscriber_id: int = Path(..., gt=0),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    result = session.get(Subscriber, subscriber_id)

    if result is not None:
        return SubscriberOut.build_instance_from_orm(result)
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent user for id={subscriber_id}'
            )


@router.put('/subscibers/{subscriber_id}', response_model=SubscriberOut)
def update_subscriber(
    subscriber_id: int = Path(..., gt=0), 
    updated_sub_info: SubscriberUpdate = Body(...),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    subscriber = session.get(Subscriber, subscriber_id)
    if subscriber is not None:
        subscriber.first_name = updated_sub_info.first_name
        subscriber.second_name = updated_sub_info.second_name
        subscriber.first_lastname = updated_sub_info.first_lastname
        subscriber.second_lastname = updated_sub_info.second_lastname
        subscriber.adress = updated_sub_info.adress
        subscriber.phone_number = updated_sub_info.phone_number
        subscriber.gender = updated_sub_info.gender.value
        
        session.commit()
        session.refresh(subscriber)

        return SubscriberOut.build_instance_from_orm(subscriber)

    else:
        raise HTTPException(
            status_code=404,
            detail='Could not update unexistent subscriber'
        )
    


@router.delete(
    '/subscibers/{subscriber_id}', 
    status_code=204,
    response_class=Response
)
def delete_subscriber(
    subscriber_id: int = Path(..., gt=0),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    subscriber = session.get(Subscriber, subscriber_id)
    if subscriber is not None:
        session.delete(subscriber)
        session.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not mark inactive unexistent subscriber id={subscriber_id}'
        )


@router.get(
    '/subscibers/{subscriber_id}/loans',
    response_model=List[LoanOut]
)
def get_subscriber_loans(
    subscriber_id: int = Path(..., gt=0),
    only_not_returned: bool = Query(False),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    filters = (
        Loan.subscriber_id == subscriber_id,
        Loan.already_returned == False if only_not_returned == True else None # Show only not returned loans
    )

    filters = filter(lambda a: True if a is not None else False, filters)

    results = session.query(Loan).filter(*filters).all()

    return list(map(LoanOut.build_instance_from_orm, results))