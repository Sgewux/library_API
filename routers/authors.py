import re
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response
from schemas.country import CountryIn, CountryOut

from schemas.enums import Gender
from models.author import Author
from models.country import Country
from schemas.author import AuthorIn, AuthorOut
from config.db import get_db_session
from models.views.all_authors_info import AllAuthorsInfo

router = APIRouter(tags=['Authors'])


@router.post('/authors', response_class=RedirectResponse)
def add_author(
    new_book: AuthorIn = Body(...),
    session: Session = Depends(get_db_session)
):
    try:
        author = Author(
            first_name = new_book.first_name.capitalize(),
            second_name = new_book.second_name.capitalize(),
            first_lastname = new_book.first_lastname.capitalize(),
            second_lastname = new_book.second_lastname.capitalize(),
            gender = new_book.gender.value,
            country_id = new_book.country
        )

        session.add(author)
        session.commit()
        session.refresh(author)

        return RedirectResponse(f'/authors/{author.id}', status_code=303)
    
    except IntegrityError as e:
        session.rollback()
        postgres_error = e.orig

        if type(postgres_error) == ForeignKeyViolation:
            raise HTTPException(
                status_code=400,
                detail='You linked the author to an unexistent country id.'
            )


@router.get('/authors', response_model=List[AuthorOut])
def get_authors(
    record_limit: int = Query(100, gt=0),
    gender: Gender | None = Query(None),
    country_name: str | None = Query(None, max_length=20),
    session: Session = Depends(get_db_session)
):
    filters = (
        AllAuthorsInfo.gender == gender.value if gender is not None else None,
        AllAuthorsInfo.country.ilike(country_name) if country_name is not None else None
    )

    filters = filter(lambda a: True if a is not None else False, filters)
    results = session.query(AllAuthorsInfo).\
              filter(*filters).limit(record_limit).all()
    authors = list(map(AuthorOut.build_instance_from_orm, results))

    return authors


@router.post('/authors/countries', response_class=RedirectResponse)
def add_country(
    new_country: CountryIn = Body(...),
    session: Session = Depends(get_db_session)
):
    try:
        # Naming country with the first letter in uppercase and the remains in lowercase
        new_country.name = re.sub('\s+', ' ', new_country.name.strip()).capitalize()
        country = Country(
            name= new_country.name
        )
        session.add(country)
        session.commit()
        session.refresh(country)

        return RedirectResponse(f'/authors/countries/{country.id}', status_code=303)
    
    except IntegrityError as e:
        session.rollback()
        postgres_error = e.orig
        
        if type(postgres_error) == UniqueViolation:
            raise HTTPException(
                status_code=400,
                detail=f'Contry with name= "{new_country}" already exists.'
            )


@router.get('/authors/countries', response_model=List[CountryOut])
def get_authors_countries(
    record_limit: int = Query(100, gt=0),
    country_name: str | None = Query(None),
    session: Session = Depends(get_db_session)
):
    q = session.query(Country)
    
    if country_name is not None:
        q = q.filter(Country.name.ilike(country_name))
    
    results = q.limit(record_limit).all()
    countries = list(map(CountryOut.build_instance_from_orm, results))

    return countries


@router.get('/authors/countries/{country_id}', response_model=CountryOut)
def get_authors_contry(
    country_id: int = Path(...),
    session: Session = Depends(get_db_session)
):
    result = session.get(Country, country_id)

    if result is not None:
        country = CountryOut.build_instance_from_orm(result)
        
        return country
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent country for id={country_id}'
        )

@router.get('/authors/{author_id}', response_model=AuthorOut)
def get_author(
    author_id: int = Path(...),
    session: Session = Depends(get_db_session)
):
    result = session.get(AllAuthorsInfo, author_id)
    if result is not None:
        author = AuthorOut.build_instance_from_orm(result)

        return author
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent author for id= {author_id}'
        )