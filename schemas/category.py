from pydantic import BaseModel, Field

from models.category import Category

class CategoryIn(BaseModel):
    name: str = Field(..., max_length=20)
    floor: int = Field(..., gt=0, le=2)
    shelf: int = Field(..., gt=0, le=10)

class CategoryOut(CategoryIn):
    id: int = Field(..., gt=0)

    @classmethod
    def build_instance_from_orm(cls, result: Category):
        new = cls(
            id = result.id,
            name = result.category_name,
            floor = result.floor,
            shelf = result.shelf_number
        )

        return new