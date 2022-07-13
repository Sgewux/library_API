from datetime import datetime

from sqlalchemy.orm import Session
from jose.exceptions import JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from .token import decode_token
from config.db import get_db_session
from models.librarian import Librarian
from schemas.auth.librarian_session import LibrarianSession


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/librarians/login')

def get_librarian_session(
    token:str = Depends(oauth2_scheme),
    session:Session = Depends(get_db_session)
    ) -> LibrarianSession:
    '''
    Obtains the JWT token from authorization header, obtains a LibrarianSession from decoding it,
    validates that session, if everything ok returns it, if not raise the HttpException
    '''
    try:
        librarian_session = decode_token(token)
        if session.get(Librarian, librarian_session.id) and (librarian_session.exp_date > datetime.utcnow()):
            return librarian_session  # Session is still alive and represents a librarian that still exists
        else:
            # Session has expired or belongs to a librarian that does not exists
            raise HTTPException(
                status_code=401,
                detail='Expired session',
                headers={'WWW-Authenticate': 'Bearer'}
            )
    except JWTError:
        # JWT token could not be vaidated (invalid signature for example)
        raise HTTPException(
                status_code=401,
                detail='Invalid credentials',
                headers={'WWW-Authenticate': 'Bearer'}
            )