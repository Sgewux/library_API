from pydantic import BaseModel, Field

from .enums import SubscriberStatus, Gender

class SubscriberIn(BaseModel):
    id: int = Field(...)
    first_name: str = Field(..., max_length=20)
    second_name: str | None = Field(None, max_length=20)
    first_lastname: str = Field(..., max_length=20)
    second_lastname: str = Field(..., max_length=20)
    adress: str = Field(..., max_length=50)
    phone_number: str = Field(..., min_length=10, max_length=10)
    gender: Gender = Field(...)


class SubscriberOut(SubscriberIn):
    '''
    Inherits all the atributes from SubscriberIn and
    adds an extra one status (ACTIVE/INACTIVE)
    this field was excluded from SubsciberIn
    because is the Database the one who will be responsible of
    managin that field.
    '''
    status: SubscriberStatus


