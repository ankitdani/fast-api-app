from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
import jwt
from dotenv import load_dotenv
import os
import models

from sqlalchemy.orm import Session
load_dotenv()
from database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM="HS256"

pwd_context = CryptContext(schemes=["bcrypt"])

def create_hash_password(plain_password: str):
    return pwd_context.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_jwt_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="users/login")),
                     db: Session = Depends(get_db)):
    user = decode_token(token)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate user credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    username = user.get("sub")
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if db_user is None:
        raise HTTPException(status_code=401,
                            detail="user not found",
                            headers={"WWW-Authenticate": "Bearer"})
    return db_user