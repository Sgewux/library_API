from pydantic import BaseModel, Field

from .author import Author

class BookLocation(BaseModel):
    floor: int
    shelf_number: int
    shelf_row_number: int


class BookOut(BaseModel):
    id: int
    book_name: str
    category: str
    author_info: Author
    location: BookLocation




