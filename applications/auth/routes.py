from fastapi import APIRouter, Depends, HTTPException, status, Body, Form
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError, ExpiredSignatureError
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from applications.user.models import User  # your Tortoise ORM/SQLModel/Pydantic model
from app.token import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM, REFRESH_SECRET_KEY

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup")
async def signup(
    username: str = Body(...),
    email: str = Body(...),
    password: str = Body(...)
):
    existing_user = await User.get_or_none(username=username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = pwd_context.hash(password)
    user = await User.create(username=username, email=email, password=hashed_password)

    return {"message": "User created successfully", "id": user.id}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await User.get_or_none(username=form_data.username)
    if not user or not pwd_context.verify(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token_data = {
        "sub": str(user.id),
        "username": user.username,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser
    }

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/forgot-password")
async def forgot_password(email: str = Body(...)):
    user = await User.get_or_none(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    token_data = {"sub": str(user.id), "type": "password_reset"}
    reset_token = jwt.encode(
        {**token_data, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {"reset_token": reset_token, "message": "Password reset token created"}



@router.post("/reset-password")
async def reset_password(token: str = Body(...), new_password: str = Body(...)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid reset token")
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token is invalid or expired")

    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password = pwd_context.hash(new_password)
    await user.save()

    return {"message": "Password has been reset successfully"}
