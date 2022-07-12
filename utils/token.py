import os
from datetime import datetime
from datetime import timedelta

from jose import jwt
from dotenv import load_dotenv

from schemas.auth.access_token import AccessTokenPayload

load_dotenv()

ALGORITHM = 'HS256'
SECRET = os.getenv('JWT_SECRET')
EXPIRE_MINUTES = 60*6 # lets say librarians have 6 hour shifts


def generate_token(payload: AccessTokenPayload) -> str:
    expiration = {
        'exp_date': (datetime.utcnow() + timedelta(minutes=EXPIRE_MINUTES)).isoformat()
    }
    return jwt.encode(
        dict(payload) | expiration, # Concat payload data with expiration data
        SECRET,
        algorithm=ALGORITHM
    )



