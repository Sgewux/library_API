from datetime import datetime
from datetime import date

from pydantic import BaseModel, Field

class LoanIn(BaseModel):
    loan_date: date | None = Field(default_factory=date.today)
    loan_exp_date: date = Field(...)
    subscriber_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)

