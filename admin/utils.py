import datetime
from pytz import timezone
import jwt
import secrets
from fastapi import status, Depends, HTTPException
from typing import Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from passlib.context import CryptContext
from pydantic import BaseModel
import models.user


utc = timezone('UTC')

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

secret_key = secrets.token_hex(32)
algorithm = "HS256"

class TokenData(BaseModel):
    username: Optional[str] = None

def load_user(username: str):  # could also be an asynchronous function
    user = models.user.find_by_username(username)
    return user

async def verify_token(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except Exception:
        raise credentials_exception
    user = load_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

def create_access_token(*, data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire =  datetime.datetime.now(tz=utc) + expires_delta
    else:
        expire =  datetime.datetime.now(tz=utc) + datetime.timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt

