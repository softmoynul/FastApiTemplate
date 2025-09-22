from fastapi import APIRouter
from jose import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

# JWT settings
SECRET_KEY = "viB2ysUJ7a91SRDPZIHWtjIUlpH-m0Ye0dnrtzsoO1M"
REFRESH_SECRET_KEY = "IeesoMBlYQjADtCqclUXr58la1ZvlRkqnfcWUNTAn4Q"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)