from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, FastAPI
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from tortoise.exceptions import DoesNotExist

from applications.user.models import User

# =========================
# JWT SETTINGS
# =========================
SECRET_KEY = "viB2ysUJ7a91SRDPZIHWtjIUlpH-m0Ye0dnrtzsoO1M"
REFRESH_SECRET_KEY = "IeesoMBlYQjADtCqclUXr58la1ZvlRkqnfcWUNTAn4Q"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

router = APIRouter()


# =========================
# TOKEN HELPERS
# =========================
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


# =========================
# AUTH HELPERS
# =========================
async def get_current_user(
    request: Request,
    token: str = Depends(oauth2_scheme),
    refresh_token: str = Form(None)  # you can also use Cookie(None)
) -> User:
    """
    Try access token first.
    If expired -> refresh with refresh_token.
    Always fetch User from DB for security.
    """
    try:
        # Try normal access token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except ExpiredSignatureError:
        if not refresh_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token expired. Refresh token required.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Try refreshing with refresh token
        try:
            refresh_payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])

            token_data = {
                "sub": refresh_payload.get("sub"),
                "username": refresh_payload.get("username"),
                "is_active": refresh_payload.get("is_active"),
                "is_staff": refresh_payload.get("is_staff"),
                "is_superuser": refresh_payload.get("is_superuser"),
            }

            new_access_token = create_access_token(token_data)
            new_refresh_token = create_refresh_token(token_data)

            # Attach new tokens to request.state so middleware can add them to response
            request.state.new_tokens = {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
            }

            # Decode new access token for payload
            payload = jwt.decode(new_access_token, SECRET_KEY, algorithms=[ALGORITHM])

        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired. Please log in again.",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from DB
    try:
        user = await User.get(id=payload.get("sub"))
    except DoesNotExist:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return user


# =========================
# ROLE DEPENDENCIES
# =========================
async def superuser_required(current_user: User = Depends(get_current_user)):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user


async def staff_required(current_user: User = Depends(get_current_user)):
    if not (current_user.is_staff or current_user.is_superuser):
        raise HTTPException(status_code=403, detail="Staff access required")
    return current_user


async def login_required(current_user: User = Depends(get_current_user)):
    return current_user


def permission_required(codename: str):
    async def wrapper(current_user: User = Depends(get_current_user)):
        if not await current_user.has_permission(codename):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{codename}' required",
            )
        return current_user
    return wrapper


# # =========================
# # MIDDLEWARE FOR NEW TOKENS
# # =========================
# app = FastAPI()

# @app.middleware("http")
# async def attach_new_tokens(request: Request, call_next):
#     response = await call_next(request)
#     if hasattr(request.state, "new_tokens"):
#         response.headers["X-New-Access-Token"] = request.state.new_tokens["access_token"]
#         response.headers["X-New-Refresh-Token"] = request.state.new_tokens["refresh_token"]
#     return response


# # =========================
# # SAMPLE ROUTES
# # =========================
# @router.get("/protected")
# async def protected_route(current_user: User = Depends(login_required)):
#     return {"message": f"Hello, {current_user.username}"}


# app.include_router(router, prefix="/auth", tags=["auth"])
