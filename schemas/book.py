from pydantic import BaseModel, Field

from .author import AuthorOut
from models.views.all_books_info import AllBooksInfo

class BookLocation(BaseModel):
    floor: int
    shelf_number: int
    shelf_row_number: int


class BookOut(BaseModel):
    id: int
    book_name: str
    available: bool
    category: str
    author_info: AuthorOut
    location: BookLocation


    @classmethod
    def build_instance_from_orm(cls, result: AllBooksInfo):
        # Gave an instance of AllBooksInfo view as argument
        # to AuthorOut.build_instance_from_orm because
        # it has all the necessary attrs to build an AuthorOut instance

        new = cls(
            id = result.id,
            book_name = result.book_name,
            available = result.available,
            category = result.category,
            author_info = AuthorOut.build_instance_from_orm(result),
            location = BookLocation(
                floor = result.floor,
                shelf_number = result.shelf_number,
                shelf_row_number = result.shelf_row_num
            )
        )

        return new


class BookIn(BaseModel):
    book_name: str = Field(..., max_length=20)
    shelf_row_number: int = Field(..., gt=0, le=10)
    category_id: int = Field(...)
    author_id: int = Field(...)