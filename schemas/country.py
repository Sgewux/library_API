from pydantic import BaseModel, Field

from models.country import Country
class CountryIn(BaseModel):
    name: str = Field(..., max_length=20)


class CountryOut(CountryIn):
    id: int = Field(..., gt=0)

    @classmethod
    def build_instance_from_orm(cls, result: Country):
        new = cls(
            id = result.id,
            name = result.name
        )

        return new

