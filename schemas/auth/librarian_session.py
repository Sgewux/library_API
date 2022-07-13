from datetime import datetime

from pydantic import BaseModel, Field

from schemas.enums import LibrarianRole

class LibrarianSession(BaseModel):
    id: int = Field(...)
    role: LibrarianRole = Field(...)
    exp_date: datetime = Field(...)