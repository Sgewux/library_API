from fastapi import APIRouter, Path, HTTPException

from config.db import session
from models.views.all_books_info import AllBooksInfo

router = APIRouter(tags=['books'])

@router.get('/books')
def get_books():
    books = []
    results = session.query(AllBooksInfo).all()
    for result in results:
        book = {
                'id': result.id,
                'book_name': result.book_name,
                'category': result.category,
                'author_info': {
                    'id': result.author_id,
                    'author_first_name': result.author_first_name,
                    'author_second_name': result.author_second_name,
                    'author_first_lastname': result.author_first_lastname,
                    'author_second_lastname': result.author_second_lastname,
                    'author_gender': result.author_gender,
                    'author_country': result.author_country
                },
                'location': {
                    'floor': result.floor,
                    'shelf_number': result.shelf_number,
                    'shelf_row_number': result.shelf_row_num
                }
            }
        books.append(book)

    return books


@router.get('/books/{book_id}')
def get_book(book_id: int = Path(... , gt=0)):
    result = session.get(AllBooksInfo, book_id)
    if result is not None:
        book = {
                'id': result.id,
                'book_name': result.book_name,
                'category': result.category,
                'author_info': {
                    'id': result.author_id,
                    'author_first_name': result.author_first_name,
                    'author_second_name': result.author_second_name,
                    'author_first_lastname': result.author_first_lastname,
                    'author_second_lastname': result.author_second_lastname,
                    'author_gender': result.author_gender,
                    'author_country': result.author_country
                },
                'location': {
                    'floor': result.floor,
                    'shelf_number': result.shelf_number,
                    'shelf_row_number': result.shelf_row_num
                }
            }

        return book

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent book for id= {book_id}'
        )
