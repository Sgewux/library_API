from typing import List
from unittest import result

from sqlalchemy import text
from fastapi import APIRouter, Path, Query, Body, HTTPException

from config.db import session, engine
from models.subscriber import Subscriber
from schemas.subscriber import SubscriberIn, SubscriberOut


router = APIRouter(tags=['Subscribers'])

@router.post('/subscribers', response_model=SubscriberOut, status_code=201)
def add_subscriber(new_subscriber: SubscriberIn = Body(...)):
    pass
    # sql = text(f'INSERT INTO \
    #     subscribers(id, first_name, second_name, first_lastname, second_lastname, adress, phone_number, gender)\
    #     VALUES ({new_subscriber.id}, {new_subscriber.first_name}, null,\
    #             {new_subscriber.first_lastname}, {new_subscriber.second_lastname},\
    #             {new_subscriber.adress}, {new_subscriber.phone_number}, {new_subscriber.gender})\
    #     ON CONFLICT(id) DO UPDATE\
    #     SET adress={new_subscriber.adress}, phone_number={new_subscriber.phone_number}, status=ACTIVE')
    
    # engine.execute(sql)


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


@router.delete('/subscibers/{subscriber_id}')
def delete_subscriber(subscriber_id: int = Path(..., gt=0)):
    session.query(Subscriber).filter(Subscriber.id == subscriber_id).delete()
    session.commit()



