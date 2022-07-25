from pydantic import BaseModel, Field, root_validator

from models.views.all_books_info import AllBooksInfo
from models.views.all_authors_info import AllAuthorsInfo
from schemas.parsing_utils.people_names import parse_names
from .enums import Gender


class AuthorIn(BaseModel):
    first_name: str = Field(..., max_length=20)
    second_name: str | None = Field(None, max_length=20)
    first_lastname: str= Field(..., max_length=20)
    second_lastname: str = Field(..., max_length=20)
    gender: Gender = Field(...)
    country: int = Field(...)

    @root_validator
    def validate_names(cls, values):
        return parse_names(values)

class AuthorOut(AuthorIn):
    id: int
    country: str = Field(..., max_length=20) # Here contry is represented as its verbose name

    @classmethod
    def build_instance_from_orm(cls, result: AllBooksInfo | AllAuthorsInfo):
        '''
        Builds an instance of AuthorOut from an instance of either
        AllAuthorsInfo or AllBooksInfo (both have the same data)
        '''

        # Creating kwargs dict 
        # (keys are AuthorOut schema fields, values are the 'result' obj attrs names that contain the data we need)
        kwargs = {
            'id': 'id',
            'first_name': 'first_name',
            'second_name': 'second_name',
            'first_lastname': 'first_lastname',
            'second_lastname': 'second_lastname',
            'gender': 'gender',
            'country': 'country'
        }

        # extracting the actual attr value
        for k, v in kwargs.items():
            if type(result) == AllBooksInfo:
                v = 'author_' + v # AllBooksInfo has the attr name with 'author_' as prefix, so we add it
            kwargs[k] = getattr(result, v)  # Obtaning the attr value from is name with getattr(obj, name)

        return cls(**kwargs)  # Bulding instance