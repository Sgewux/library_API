from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from psycopg2.errors import ForeignKeyViolation
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends

from models.book import Book
from schemas.enums import Gender
from config.db import get_db_session
from models.views.all_books_info import AllBooksInfo
from schemas.book import BookIn, BookOut


router = APIRouter(tags=['Books'])

@router.get('/books', response_model=List[BookOut])
def get_books(
    record_limit: int = Query(100, gt=0),
    book_name: str | None = Query(None),
    author_gender: Gender | None = Query(None),
    floor: int | None = Query(None, gt=0, le=2),
    shelf_number: int | None = Query(None, gt=0, le=10),
    shelf_row_number: int | None = Query(None, gt=0, le=10),
    session: Session = Depends(get_db_session)
):
    # Creating a tupe which will contain the SQL filters if the query param was provided
    # and None if the query param was NOT provided
    filters = (
        AllBooksInfo.book_name.ilike(f'%{book_name}%') if book_name is not None else None,
        AllBooksInfo.author_gender == author_gender.value if author_gender is not None else None,
        AllBooksInfo.shelf_number == shelf_number if shelf_number is not None else None,
        AllBooksInfo.floor == floor if floor is not None else None,
        AllBooksInfo.shelf_row_num == shelf_row_number if shelf_row_number is not None else None
    )

    # Removing all None values from the filters iterable to make it ready to be
    # depackaged with '*' so as to give all its elements as query.filter() arguments
    filters = filter(lambda a: True if a is not None else False, filters)

    results = session.query(AllBooksInfo).\
              filter(*filters).limit(record_limit).all()  # Notice the '*' before 'filters'
    
    books = list(map(BookOut.build_instance_from_orm, results))

    return books


@router.get('/books/{book_id}', response_model=BookOut)
def get_book(
    book_id: int = Path(... , gt=0), 
    session: Session = Depends(get_db_session)
):

    result = session.get(AllBooksInfo, book_id)

    if result is not None:
        book = BookOut.build_instance_from_orm(result)

        return book

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent book for id= {book_id}'
        )


@router.post('/books', status_code=201)
def add_book(
    new_book: BookIn = Body(...),
    session: Session = Depends(get_db_session)
):
    book = Book(
        book_name = new_book.book_name,
        shelf_row_num = new_book.shelf_row_number,
        category_id = new_book.category_id,
        author_id = new_book.author_id
    )

    try:
        session.add(book)
        session.commit()

        session.refresh(book)  # Refreshing instance atributes
        
        # Redirecting with 303 as status code to make a GET request insted of a POST one
        # Leaving 307 (default) will perform a request with same method and same body
        return RedirectResponse(f'/books/{book.id}', status_code=303)

    except IntegrityError as e:
        session.rollback()
        postgres_error = e.orig  # The psycopg2 error wrapped by interity error
        if type(postgres_error) == ForeignKeyViolation:
            raise HTTPException(
                status_code=400,
                detail='You linked your book to either an unexistent Category id or an unexistent author id'
                )