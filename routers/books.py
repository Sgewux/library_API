import re
from typing import List

from sqlalchemy import text
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError, InternalError
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from models.book import Book
from schemas.enums import Gender
from config.db import get_db_session, engine
from utils.auth import get_librarian_session
from models.views.all_books_info import AllBooksInfo
from schemas.book import BookIn, BookOut


router = APIRouter(tags=['Books'])

@router.get('/books', response_model=List[BookOut])
def get_books(
    record_limit: int = Query(100, gt=0),
    only_available: bool = Query(True),
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
        AllBooksInfo.available == True if only_available == True else None,
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
    

    return list(map(BookOut.build_instance_from_orm, results))


@router.get('/books/{book_id}', response_model=BookOut)
def get_book(
    book_id: int = Path(... , gt=0), 
    session: Session = Depends(get_db_session)
):

    result = session.get(AllBooksInfo, book_id)

    if result is not None:
        return  BookOut.build_instance_from_orm(result)

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent book for id= {book_id}'
        )


@router.post('/books', response_class=RedirectResponse)
def add_book(
    new_book: BookIn = Body(...),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    # Removing leading spaces and double spaces between the words from book name
    new_book.book_name = re.sub('\s+', ' ', new_book.book_name.strip()).capitalize()

    try:
        # Using raw SQL because the ORM was missbehaving due to a before insert database trigger.
        sql = text(f"INSERT INTO books(book_name, shelf_row_num, category_id, author_id)\
                    VALUES('{new_book.book_name}', {new_book.shelf_row_number}, \
                           {new_book.category_id}, {new_book.author_id}) RETURNING id")

        result = engine.execute(sql)
        new_id = result.first()

        if new_id is not None:
            # If a completly new book was added to the database.
            return RedirectResponse(f'/books/{new_id[0]}', status_code=303)
        else:
            # If the "new" book was already registered BUT marked as not available (softdeleted)
            # then no id is returned from the insert (because no inserts were performed) due to
            # a database trigger that was made for dealing with this "reinsert" operations
            result = session.query(Book).filter(Book.book_name.ilike(new_book.book_name)).first()
            return RedirectResponse(f'/books/{result.id}', status_code=303)

    except IntegrityError as e:
        session.rollback()
        postgres_error = e.orig  # The psycopg2 error wrapped by interity error
        if type(postgres_error) == ForeignKeyViolation:
            raise HTTPException(
                status_code=422,
                detail='You linked the book to either an unexistent Category id or an unexistent author id'
                )
    
    except InternalError as e:
        session.rollback()
        postgres_error = e.orig
        
        raise HTTPException(
            status_code=422,
            detail=str(postgres_error).split('\n')[0]
        )


@router.put(
    '/books/{book_id}',
    status_code=200,
    response_model=BookOut
)
def update_book(
    book_id: int = Path(..., gt=0),
    updated_book_info: BookIn = Body(...),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    book = session.get(Book, book_id)
    if book is not None:
        try: 
            book.book_name = updated_book_info.book_name
            book.shelf_row_num = updated_book_info.shelf_row_number
            book.category_id = updated_book_info.category_id
            book.author_id = updated_book_info.author_id

            session.commit()

            # Obtaining all the updated book data from AllBooksInfo view
            return BookOut.build_instance_from_orm(
                    session.get(AllBooksInfo, book.id)
                    )

        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig  # The psycopg2 error wrapped by interity error
            if type(postgres_error) == ForeignKeyViolation:
                raise HTTPException(
                status_code=422,
                detail='You linked your book to either an unexistent Category id or an unexistent author id'
            )

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not update unexistent book id={book_id}'
        )


@router.delete(
    '/books/{book_id}', 
    status_code=204, 
    response_class=Response
)
def delete_book(
    book_id: int = Path(..., gt=0),
    _ = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    book = session.get(Book, book_id)
    if book is not None:
        session.delete(book)
        session.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not remove from inventory unexistent book id={book_id}'
        )