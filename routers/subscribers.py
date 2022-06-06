from typing import List

from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Path, Query, Body, HTTPException


from config.db import session
from models.subscriber import Subscriber
from schemas.subscriber import SubscriberIn, SubscriberOut


router = APIRouter(tags=['Subscribers'])

@router.post('/subscribers', response_model=SubscriberOut, status_code=201)
def add_subscriber(new_subscriber: SubscriberIn = Body(...)):
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
                status_code=400,
                detail=f'Phone number {subscriber.phone_number} is an already used phone number'
            )


@router.get('/subscribers', response_model=List[SubscriberOut])
def get_subscribers(only_active: bool = Query(True)):
    q = session.query(Subscriber)
    if only_active:
        q = q.filter(Subscriber.status == 'ACTIVE')
    
    results = q.all()
    subscribers = []
    
    for result in results:
        subscriber = SubscriberOut(
            id = result.id,
            first_name = result.first_name,
            second_name = result.second_name,
            first_lastname = result.first_lastname,
            second_lastname = result.second_lastname,
            adress = result.adress,
            phone_number = result.phone_number,
            gender = result.gender,
            status = result.status
        )

        subscribers.append(subscriber)
    
    return subscribers


@router.get('/subscribers/{subscriber_id}', response_model=SubscriberOut)
def get_subscriber(subscriber_id: int = Path(..., gt=0)):
    result = session.get(Subscriber, subscriber_id)

    if result is not None:
        subscriber = SubscriberOut(
            id = result.id,
            first_name = result.first_name,
            second_name = result.second_name,
            first_lastname = result.first_lastname,
            second_lastname = result.second_lastname,
            adress = result.adress,
            phone_number = result.phone_number,
            gender = result.gender,
            status = result.status
        )

        return subscriber
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistenr user for id={subscriber_id}'
            )


@router.put('/subscibers/{subscriber_id}')
def update_subscriber(
    subscriber_id: int = Path(..., gt=0), 
    updated_sub_info: SubscriberIn.exclude('id') = Body(...)
):
    pass


@router.delete('/subscibers/{subscriber_id}')
def delete_subscriber(subscriber_id: int = Path(..., gt=0)):
    session.query(Subscriber).filter(Subscriber.id == subscriber_id).delete()
    session.commit()