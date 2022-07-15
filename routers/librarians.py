from sqlalchemy.orm import Session
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
    response_model_exclude=['access_password']
    )
def register_librarian(
    librarian_info:LibrarianIn  = Body(...),
    librarian_session: LibrarianSession = Depends(get_librarian_session),
    session: Session = Depends(get_db_session)
):
    if librarian_session.role == LibrarianRole.SUPERVISOR:
        librarian = Librarian(
            id = librarian_info.id,
            first_name = librarian_info.first_name.capitalize(),
            second_name = librarian_info.second_name.capitalize(),
            first_lastname = librarian_info.first_lastname.capitalize(),
            second_lastname = librarian_info.second_lastname.capitalize(),
            role = librarian_info.role.value,
            access_password = hash_password(librarian_info.access_password) # Storing hashed password
        )

        session.add(librarian)
        session.commit()
        session.refresh(librarian)

        return LibrarianIn.build_instance_from_orm(librarian)
    
    else:
        raise HTTPException(
            status_code=403,
            detail='Only librarians with SUPERVISOR role can register librarians in the system.'
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