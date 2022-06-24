import re
from typing import List
from unicodedata import category

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi.responses import RedirectResponse
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from config.db import get_db_session
from models.category import Category
from schemas.category import CategoryIn, CategoryOut

router = APIRouter(tags=['Categories'])

@router.post('/categories', response_class=RedirectResponse)
def add_category(
    new_category: CategoryIn = Body(...),
    session: Session = Depends(get_db_session)
):
    new_category.name = re.sub('\s+', ' ', new_category.name.strip()).capitalize()
    category = Category(
        category_name=new_category.name,
        floor=new_category.floor,
        shelf_number=new_category.shelf
    )

    try:
        session.add(category)
        session.commit()
        session.refresh(category)

        return RedirectResponse(f'/categories/{category.id}', status_code=303)
    except IntegrityError as e:
        postgres_error = e.orig
        if type(postgres_error) == UniqueViolation:
            if 'categories_floor_shelf_number_key' in postgres_error.pgerror:
                raise HTTPException(
                    status_code=400,
                    detail=f'There is already a category with:\
                        Floor= {category.floor} and Shelf_number= {category.shelf_number}. \
                        Please assing a different location for the new cateogory.'
                )
            elif 'categories_category_name_key' in postgres_error.pgerror:
                raise HTTPException(
                    status_code=400,
                    detail=f'There is already a category with name= {category.category_name}'
                )

@router.get('/categories', response_model=List[CategoryOut])
def get_categories(
    record_limit: int = Query(10, gt=0),
    floor_number: int|None = Query(None, gt=0, le=2),
    name: str|None = Query(None, max_length=20),
    session: Session = Depends(get_db_session)
):
    filters = (
        Category.floor == floor_number if floor_number is not None else None,
        Category.category_name.ilike(name) if name is not None else None
    )

    filters = filter(lambda a: True if a is not None else False, filters)

    results = session.query(Category).\
              filter(*filters).limit(record_limit).all()
    
    return list(map(CategoryOut.build_instance_from_orm, results))


@router.get('/categories/{category_id}')
def get_category(
    category_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session)
):
    result = session.get(Category, category_id)

    if result is not None:
        return CategoryOut.build_instance_from_orm(result)
    else:
        raise HTTPException(
            status_code=404,
            detail=f'Unexistent category id= {category_id}'
        )


@router.put('/categories/{category_id}')
def update_category(
    category_id: int = Path(..., gt=0),
    updated_category_info: CategoryIn = Body(...),
    session: Session = Depends(get_db_session)
):
    category = session.get(Category, category_id)
    if category is not None:
        try:
            updated_category_info.name =  re.sub(
                '\s+', ' ', updated_category_info.name.strip()
                ).capitalize()

            category.category_name = updated_category_info.name
            category.floor = updated_category_info.floor
            category.shelf_number = updated_category_info.shelf

            session.commit()
            session.refresh(category)

            return CategoryOut.build_instance_from_orm(category)

        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig
            if type(postgres_error) == UniqueViolation:
                if 'categories_floor_shelf_number_key' in postgres_error.pgerror:
                    raise HTTPException(
                        status_code=400,
                        detail=f'There is already a category with:\
                        Floor= {updated_category_info.floor} and Shelf_number= {updated_category_info.shelf}. \
                        Please assing a different location for the cateogory.'
                    )
                elif 'categories_category_name_key' in postgres_error.pgerror:
                    raise HTTPException(
                        status_code=400,
                        detail=f'There is already a category with name= {updated_category_info.name}'
                    )

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not delete unexistent category id= {category_id}'
        )


@router.delete(
    '/categories/{category_id}', 
    status_code=204, 
    response_class=Response
)
def delete_category(
    category_id: int = Path(..., gt=0),
    session: Session = Depends(get_db_session)
):
    category = session.get(Category, category_id)
    if category is not None:
        try:
            session.delete(category)
            session.commit()
        except IntegrityError as e:
            session.rollback()
            postgres_error = e.orig
            if type(postgres_error) == ForeignKeyViolation:
                raise HTTPException(
                    status_code=400,
                    detail=f'Category "{category.category_name}" is still referenced by books'
                )

    else:
        raise HTTPException(
            status_code=404,
            detail=f'Could not delete unexistent category id= {category_id}'
        )
    