from datetime import datetime
from datetime import date
from xmlrpc.client import boolean

from pydantic import BaseModel, Field

from models.loan import Loan


class LoanIn(BaseModel):
    loan_date: date | None = Field(default_factory=date.today)
    loan_exp_date: date = Field(...)
    subscriber_id: int = Field(..., gt=0)
    book_id: int = Field(..., gt=0)

class LoanOut(LoanIn):
    already_returned: boolean
    id: int = Field(..., gt=0)

    @classmethod
    def build_instance_from_orm(cls, result: Loan):
        new = cls(
            id = result.id,
            loan_date = result.loan_date,
            loan_exp_date = result.loan_exp_date,
            subscriber_id = result.subscriber_id,
            book_id = result.book_id,
            already_returned = result.already_returned
        )

        return new
