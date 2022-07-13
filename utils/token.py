import os
from datetime import datetime
from datetime import timedelta

from jose import jwt
from dotenv import load_dotenv
from schemas.auth.access_token import AccessToken

from schemas.auth.librarian_session import LibrarianSession
from schemas.enums import LibrarianRole

load_dotenv()

ALGORITHM = 'HS256'
SECRET = os.getenv('JWT_SECRET')
EXPIRE_MINUTES = 60*6 # lets say librarians have 6 hour shifts


def generate_token(payload: dict) -> AccessToken:
    '''
    Recieves payload data in shape of dict, adds expiration date to the session
    and then creates and returns a string representing JWT
    '''
    expiration = {
        'exp_date': (datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)).isoformat()
    }
    token = jwt.encode(
        payload | expiration, # Concat payload data with expiration data
        SECRET,
        algorithm=ALGORITHM
    )

    return AccessToken(
        access_token=token
    )


def decode_token(token:str) -> LibrarianSession:
    '''
    Recieves a string representing JWT token, decode its content
    casts its values to a proper ones (obtains the proper enum instance by its value,
    obtians a datetime python object by its iso string representation, converts id into int), then
    builds an instance of LibrarianSession pydantic schema
    '''
    decoded_token = jwt.decode(token, SECRET, algorithms=[ALGORITHM])

    return LibrarianSession(
        id = int(decoded_token['sub']),
        role = getattr(LibrarianRole, decoded_token['role']),
        exp_date = datetime.fromisoformat(decoded_token['exp_date'])
    )




