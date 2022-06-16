from pydantic import BaseModel, Field

from .author import AuthorOut
from models.views.all_books_info import AllBooksInfo

class BookLocation(BaseModel):
    floor: int = Field(..., le=2)
    shelf_number: int = Field(..., le=10)
    shelf_row_number: int = Field(..., le=10)


class BookOut(BaseModel):
    id: int = Field(..., gt=0)
    book_name: str = Field(..., max_length=20)
    available: bool = Field(...)
    category: str = Field(..., max_length=20)
    author_info: AuthorOut = Field(...)
    location: BookLocation = Field(...)


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