from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError, ExpiredSignatureError

# JWT settings
SECRET_KEY = "viB2ysUJ7a91SRDPZIHWtjIUlpH-m0Ye0dnrtzsoO1M"
REFRESH_SECRET_KEY = "IeesoMBlYQjADtCqclUXr58la1ZvlRkqnfcWUNTAn4Q"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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


async def verify_token(token: str = Depends(oauth2_scheme), refresh_token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return {"valid": True, "payload": payload}

    except ExpiredSignatureError:
        if not refresh_token:
            return {"valid": False, "message": "Access token expired. Refresh token required."}

        try:
            refresh_payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])

            token_data = {
                "sub": refresh_payload.get("sub"),
                "username": refresh_payload.get("username"),
                "is_active": refresh_payload.get("is_active"),
                "is_staff": refresh_payload.get("is_staff"),
                "is_superuser": refresh_payload.get("is_superuser")
            }

            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)

            return {
                "valid": True,
                "message": "Access token refreshed",
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "payload": jwt.decode(new_access_token, SECRET_KEY, algorithms=[ALGORITHM])
            }

        except ExpiredSignatureError:
            return {"valid": False, "message": "Refresh token expired. Please log in again."}
        except JWTError:
            return {"valid": False, "message": "Invalid refresh token"}

    except JWTError:
        return {"valid": False, "message": "Invalid access token"}


async def superuser_required(token_data: dict = Depends(verify_token)):
    if not token_data["valid"]:
        raise HTTPException(status_code=401, detail=token_data["message"])

    payload = token_data["payload"]
    if not payload.get("is_active", False):
        raise HTTPException(status_code=401, detail="User is inactive")

    if not payload.get("is_superuser", False):
        raise HTTPException(status_code=403, detail="Superuser access required")

    return payload


async def staff_required(token_data: dict = Depends(verify_token)):
    if not token_data["valid"]:
        raise HTTPException(status_code=401, detail=token_data["message"])

    payload = token_data["payload"]

    if not payload.get("is_active", False):
        raise HTTPException(status_code=401, detail="User is inactive")

    if not (payload.get("is_staff", False) or payload.get("is_superuser", False)):
        raise HTTPException(status_code=403, detail="Staff access required")

    return payload

async def login_required(token_data: dict = Depends(verify_token)):
    if not token_data["valid"]:
        raise HTTPException(status_code=401, detail=token_data["message"])

    payload = token_data["payload"]
    return payload