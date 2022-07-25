import re

from pydantic import BaseModel, Field, validator, root_validator

from models.librarian import Librarian
from schemas.parsing_utils.people_names import parse_names
from schemas.enums import LibrarianRole

class LibrarianIn(BaseModel):
    id: int = Field(..., gt=0)
    first_name: str = Field(..., max_length=20)
    second_name: str | None = Field(None, max_length=20)
    first_lastname: str = Field(..., max_length=20)
    second_lastname: str = Field(..., max_length=20)
    role: LibrarianRole = Field(...)
    access_password: str = Field(..., min_length=8)

    @root_validator
    def validate_names(cls, values):
        return parse_names(values)

    @validator('access_password')
    def is_secure_password(cls, password):
        conditionals = (
            re.compile('[#\$%=!¡\?¿]+').search(password), # At least one special character
            re.compile('[A-Z]+').search(password) # At least one capital letter
        )

        if all(conditionals):
            return password
        else:
            raise ValueError(
                'Password must contain at least one char between [#$%=!¡?¿] and one capital letter.'
            )
    
    @classmethod
    def build_instance_from_orm(cls, result: Librarian):
        return cls(
            id = result.id,
            first_name = result.first_name,
            second_name = result.second_name,
            first_lastname = result.first_lastname,
            second_lastname = result.second_lastname,
            role = result.role,
            access_password = result.access_password
        )