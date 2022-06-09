from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from schemas.enums import Gender
from models.author import Author
from schemas.author import AuthorOut
from config.db import get_db_session
from models.views.all_authors_info import AllAuthorsInfo

router = APIRouter(tags=['Authors'])

@router.get('/authors', response_model=List[AuthorOut])
def get_authors(
    record_limit: int = Query(100, gt=0),
    gender: Gender | None = Query(None),
    country_name: str | None = Query(None, max_length=20),
    session: Session = Depends(get_db_session)
):
    filters = (
        AllAuthorsInfo.gender == gender.value if gender is not None else None,
        AllAuthorsInfo.country.ilike('country_name') if country_name is not None else None
    )

    filters = filter(lambda a: True if a is not None else False, filters)

    results = session.query(AllAuthorsInfo).\
              filter(*filters).limit(record_limit).all()

    authors = list(map(AuthorOut.build_instance_from_orm, results))

    return authors