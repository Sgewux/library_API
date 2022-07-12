from pydantic import BaseModel, Field, validator

from schemas.enums import LibrarianRole

class AccessToken(BaseModel):
    access_token: str = Field(...)
    token_type: str | None = Field('bearer')

class AccessTokenPayload(BaseModel):
    sub: str = Field(...)
    role: LibrarianRole = Field(...)

    @validator('sub')
    def is_numeric_str(cls, v: str) -> int:
        int(v) # Raises ValueError if str was not int str
        # i didnt use something like str.isdigit() because it did not ensure all digits were integer

        return v
    
    @validator('role')
    def get_str_value(cls, v: LibrarianRole) -> str:
        return v.value

    
