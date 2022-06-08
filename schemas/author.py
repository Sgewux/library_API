from pydantic import BaseModel, Field

from .enums import Gender
from models.author import Author

class AuthorIn(BaseModel):
    first_name: str
    second_name: str | None
    first_lastname: str
    second_lastname: str
    gender: Gender
    country: str


class AuthorOut(AuthorIn):
    id: int

    @classmethod
    def build_instance_from_orm(cls, result: Author):
        new = cls(
                id = result.author_id,
                first_name = result.author_first_name,
                second_name = result.author_second_name,
                first_lastname = result.author_first_lastname,
                second_lastname = result.author_second_lastname,
                gender = result.author_gender,
                country = result.author_country
            )
        
        return new