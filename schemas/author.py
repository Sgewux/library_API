from pydantic import BaseModel, Field

from .enums import Gender

class Author(BaseModel):
    id: int
    first_name: str
    second_name: str | None
    first_lastname: str
    second_lastname: str
    gender: Gender
    country: str
    
