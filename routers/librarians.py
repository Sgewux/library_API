from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response

from config.db import get_db_session
from schemas.enums import LibrarianRole
from utils.token import generate_token
from models.librarian import Librarian
from schemas.librarian import LibrarianIn
from utils.auth import get_librarian_session
from utils.passwords import verify_password, hash_password
from schemas.auth.librarian_session import LibrarianSession

router = APIRouter(tags=['Librarians'])

@router.post(
    '/librarians', response_model=LibrarianIn, 
    response_model_exclude=['access_password'],
    status_code=201
    )
def register_librarian(
    librarian_info:LibrarianIn  = Body(...),
    librarian_session: LibrarianSession = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    if librarian_session.role == LibrarianRole.SUPERVISOR:
        try:

            librarian = Librarian(
                id = librarian_info.id,
                first_name = librarian_info.first_name.capitalize(),
                second_name = librarian_info.second_name.capitalize() if librarian_info.second_name is not None else None,
                first_lastname = librarian_info.first_lastname.capitalize(),
                second_lastname = librarian_info.second_lastname.capitalize(),
                role = librarian_info.role.value,
                access_password = hash_password(librarian_info.access_password) # Storing hashed password
            )

            session.add(librarian)
            session.commit()
            session.refresh(librarian)

            return LibrarianIn.build_instance_from_orm(librarian)
        except IntegrityError as e:
            session.rollback()

            postgres_error = e.orig
            if type(postgres_error) == UniqueViolation:
                raise HTTPException(
                    status_code=422,
                    detail=f'Librarian with id = {librarian_info.id} is already registered.'
                )
        
    else:
        raise HTTPException(
            status_code=403,
            detail='Only librarians with SUPERVISOR role can register librarians in the system.'
        )


@router.get(
    '/librarians/{librarian_id}',
    response_model=LibrarianIn,
    response_model_exclude=['access_password']    
)
def get_librarian(
    librarian_id: int = Path(..., gt=0),    
    librarian_session: LibrarianSession = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    if librarian_session.role == LibrarianRole.SUPERVISOR:
        librarian = session.get(Librarian, librarian_id)
        if librarian_id is not None:
            return LibrarianIn.build_instance_from_orm(librarian)
        else:
            raise HTTPException(
                status_code=404,
                detail=f'Unexistent librarian for id = {librarian_id}'
            )
    else:
        raise HTTPException(
            status_code=403,
            detail='Only librarians with SUPERVISOR role can query other librarians information.'
        )


@router.put(
    '/librarians/{librarian_id}',
    response_model=LibrarianIn,
    response_model_exclude=['access_password']
)
def update_librarian_info(
    librarian_id: int = Path(..., gt=0),
    updated_librarian_info: LibrarianIn = Body(...),
    librarian_session: LibrarianSession = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    if librarian_session.id == librarian_id:
        librarian = session.get(Librarian, librarian_id)

        librarian.first_name = updated_librarian_info.first_name.capitalize()
        librarian.second_name = updated_librarian_info.second_lastname.capitalize() if updated_librarian_info.second_name is not None else None
        librarian.first_lastname = updated_librarian_info.first_lastname.capitalize()
        librarian.second_lastname = updated_librarian_info.second_lastname.capitalize()
        librarian.role = updated_librarian_info.role.value
        librarian.access_password = hash_password(updated_librarian_info.access_password)

        session.commit()
        session.refresh(librarian)

        return LibrarianIn.build_instance_from_orm(librarian)
    else:
        raise HTTPException(
            status_code=403,
            detail='Only the librarian itself is allowed to edit its info.'
        )


@router.delete(
    '/librarians/{librarian_id}',
    response_class=Response,
    status_code=204
)
def remove_librarian(
    librarian_id: int = Path(..., gt=0),
    librarian_session: LibrarianSession = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    if librarian_session.role == LibrarianRole.SUPERVISOR:
        librarian = session.get(Librarian, librarian_id)
        if librarian is not None:
            session.delete(librarian)
            session.commit()
        else:
            raise HTTPException(
                status_code=404,
                detail=f'Could not remove unexistent librarian id = {librarian_id}'
            )

    else:
        raise HTTPException(
            status_code=403,
            detail='Only librarians with SUPERVISOR role can remove other librarians from database.'
        )


@router.post('/librarians/login')
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db_session)    
):
    librarian = session.get(Librarian, int(credentials.username))

    if librarian is not None and verify_password(credentials.password, librarian.access_password):
        return generate_token({
            'sub': credentials.username,
            'role': librarian.role
        })
    else:
        raise HTTPException(
            status_code=401,
            detail='Invalid id or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )