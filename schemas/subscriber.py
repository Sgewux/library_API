from typing import Iterable

from pydantic import BaseModel, Field, create_model

from models.subscriber import Subscriber
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

    @classmethod
    def exclude(cls, *fields_to_exclude: Iterable[str]) -> BaseModel:
        '''
        Obtain a newly defined model with all the fields of this model but
        the ones in fields_to_exclude parameter
        '''

        field_definition = {}
        model_fields = cls.__fields__

        for fieldname, field in model_fields.items():
            if fieldname not in fields_to_exclude:
                if field.required:
                    field_definition[fieldname] = (field.outer_type_, ...)
                else:
                    field_definition[fieldname] = (field.outer_type_, field.default)

        new_model = create_model(
            __model_name = f'{cls.__name__}_without_{"_".join(fields_to_exclude)}',
            __base__=BaseModel,
            **field_definition
        )

        return new_model


class SubscriberOut(SubscriberIn):
    '''
    Inherits all the atributes from SubscriberIn and
    adds an extra one status (ACTIVE/INACTIVE)
    this field was excluded from SubsciberIn
    because is the Database the one who will be responsible of
    managin that field.
    '''
    status: SubscriberStatus

    @classmethod
    def build_instance_from_orm(cls, result: Subscriber):
        new = cls(
            id = result.id,
            first_name = result.first_name,
            second_name = result.second_name,
            first_lastname = result.first_lastname,
            second_lastname = result.second_lastname,
            adress = result.adress,
            phone_number = result.phone_number,
            gender = result.gender,
            status = result.status
        )

        return new




