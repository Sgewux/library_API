from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Path, Query, Body, HTTPException, Depends, Response
from models.librarian import Librarian
from schemas.auth.librarian_session import LibrarianSession

from utils.auth import get_librarian_session
from utils.token import generate_token
from config.db import get_db_session

router = APIRouter(tags=['Librarians'])

@router.post('/librarians')
def register_librarian(
    librarian_info = Body(...),
    session: Session = Depends(get_db_session)
):
    pass


@router.post('/librarians/login')
def login(
    credentials: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_db_session)    
):
    librarian = session.get(Librarian, int(credentials.username))
    # I know i should not store plain text passwords, i will hash them 
    if librarian is not None and librarian.access_password == credentials.password:
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


@router.get('/librarians/me')
def me(librarian: LibrarianSession = Depends(get_librarian_session)):
    return librarian