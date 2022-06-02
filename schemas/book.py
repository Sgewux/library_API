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


class BookIn(BaseModel):
    book_name: str = Field(..., max_length=20)
    shelf_row_number: int = Field(..., gt=0, le=10)
    category_id: int = Field(...)
    author_id: int = Field(...)