import re
from typing import List
from pydantic import PostgresDsn

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from psycopg2.errors import ForeignKeyViolation, UniqueViolation
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response
from schemas.book import BookOut
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
def get_countries(
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
def get_country(
    country_id: int = Path(...),
    session: Session = Depends(get_db_session)
):
    result = session.get(Country, country_id)

    if result is not None:
        
        return CountryOut.build_instance_from_orm(result)
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent country for id={country_id}'
        )


@router.put('/authors/countries/{country_id}', response_model=CountryOut)
def update_country(
    country_id: int = Path(..., gt=0),
    updated_country_info: CountryIn = Body(...),
    session: Session = Depends(get_db_session)
):
    country = session.get(Country, country_id)
    
    if country is not None:
        updated_country_info.name = re.sub(
            '\s+', ' ', updated_country_info.name.strip()
            ).capitalize()

        country.name = updated_country_info.name
        session.commit()
        session.refresh(country)

        return CountryOut.build_instance_from_orm(country)
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not update unexistent cube for id= {country_id}'
        )


@router.delete(
    '/authors/countries/{country_id}', 
    response_class=Response,
    status_code=204
)
def delete_country(
    country_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session)
):
    country = session.get(Country, country_id)
    if country is not None:
        try:
            session.delete(country)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig
            
            if type(postgres_error) == ForeignKeyViolation:
                raise HTTPException(
                    status_code=400,
                    detail=f'Country "{country.name}" is still referenced by authors.'
                )
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not delete an unexistent Country id= {country_id}'
        )


@router.get('/authors/{author_id}', response_model=AuthorOut)
def get_author(
    author_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session)
):
    result = session.get(AllAuthorsInfo, author_id)
    if result is not None:
      
        return AuthorOut.build_instance_from_orm(result)
    
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent author for id= {author_id}'
        )


@router.put('/authors/{author_id}', response_model=AuthorOut)
def update_author(
    author_id: int = Path(..., gt=0),
    updated_author_info: AuthorIn = Body(...),
    session: Session = Depends(get_db_session)
):
    author = session.get(Author, author_id)

    if author is not None:
        try:
            author.first_name = updated_author_info.first_name.capitalize()
            author.second_name = updated_author_info.second_name.capitalize()
            author.first_lastname = updated_author_info.first_lastname.capitalize()
            author.second_lastname = updated_author_info.second_lastname.capitalize()
            author.gender = updated_author_info.gender.value
            author.country_id = updated_author_info.country

            session.commit()

            return AuthorOut.build_instance_from_orm(
                session.get(AllAuthorsInfo, author.id)
            )

        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig
            if type(postgres_error) == ForeignKeyViolation:
                raise HTTPException(
                    status_code=400,
                    detail=f'The author was linked to an unexistent country id= {updated_author_info.country}'
                )
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not udpate unexistent Author id= {author_id}'
        )


@router.delete(
    '/authors/{author_id}',
    response_class=Response,
    status_code=204
)
def delete_author(
    author_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session)
):
    author = session.get(Author, author_id)
    if author is not None:
        try:
            session.delete(author)
            session.commit()
            
        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig
            if type(postgres_error) == ForeignKeyViolation:
                raise HTTPException(
                    status_code=400,
                    detail=f'Author id= {author.id} is still referenced by Books.'
                )