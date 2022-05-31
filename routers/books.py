from typing import List

from fastapi import APIRouter, Path, Query, HTTPException

from config.db import session
from schemas.enums import Gender
from schemas.author import Author
from schemas.book import BookOut, BookLocation
from models.views.all_books_info import AllBooksInfo

router = APIRouter(tags=['books'])

@router.get('/books', response_model=List[BookOut])
def get_books(
    record_limit: int = Query(100, gt=0),
    author_gender: Gender | None = Query(None),
    floor: int | None = Query(None, gt=0, le=2),
    shelf_number: int | None = Query(None, gt=0, le=10),
    shelf_row_number: int | None = Query(None, gt=0, le=10)
):

    books = []
    q = session.query(AllBooksInfo)

    if author_gender:
        q = q.filter(AllBooksInfo.author_gender == author_gender.value)
    if shelf_number:
        q = q.filter(AllBooksInfo.shelf_number == shelf_number)
    if floor:
        q = q.filter(AllBooksInfo.floor == floor)
    if shelf_row_number:
        q = q.filter(AllBooksInfo.shelf_row_num == shelf_row_number)

    results = q.limit(record_limit).all()
    
    for result in results:
        book = BookOut(
            id = result.id,
            book_name = result.book_name,
            category = result.category,
            author_info = Author(
                id = result.author_id,
                first_name = result.author_first_name,
                second_name = result.author_second_name,
                first_lastname = result.author_first_lastname,
                second_lastname = result.author_second_lastname,
                gender = result.author_gender,
                country = result.author_country
            ),
            location = BookLocation(
                floor = result.floor,
                shelf_number = result.shelf_number,
                shelf_row_number = result.shelf_row_num
            )
        )

        books.append(book)

    return books


@router.get('/books/{book_id}', response_model=BookOut)
def get_book(book_id: int = Path(... , gt=0)):

    result = session.get(AllBooksInfo, book_id)

    if result is not None:
        book = BookOut(
            id = result.id,
            book_name = result.book_name,
            category = result.category,
            author_info = Author(
                id = result.author_id,
                first_name = result.author_first_name,
                second_name = result.author_second_name,
                first_lastname = result.author_first_lastname,
                second_lastname = result.author_second_lastname,
                gender = result.author_gender,
                country = result.author_country
            ),
            location = BookLocation(
                floor = result.floor,
                shelf_number = result.shelf_number,
                shelf_row_number = result.shelf_row_num
            )
        )

        return book

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent book for id= {book_id}'
        )
