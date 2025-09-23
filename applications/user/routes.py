from fastapi import APIRouter, HTTPException, status, Depends, Form, Query
from app.token import superuser_required, login_required
from applications.user.models import User
from passlib.context import CryptContext
router = APIRouter(
    tags=["Users"],
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(
    username: str = Form(..., description="Username"),
    email: str = Form(..., description="Email"),
    password: str = Form(..., min_length=8, description="User password", password=True, example="********"),
    is_active: bool = Form(True),
    is_staff: bool = Form(False),
    is_superuser: bool = Form(False),
    current_user=Depends(superuser_required)
):
    if await User.filter(email=email).exists():
        raise HTTPException(status_code=400, detail="Email already registered")
    if await User.filter(username=username).exists():
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = pwd_context.hash(password)
    new_user = await User.create(
        username=username,
        email=email,
        password=hashed_password,
        is_active=is_active,
        is_staff=is_staff,
        is_superuser=is_superuser
    )
    return {
        "message": f"{current_user['username']} created this user",
        "new_user": new_user
    }

@router.get("/users", status_code=status.HTTP_200_OK, dependencies=[Depends(login_required)])
async def get_all_users():
    return await User.all().values(
        "id", "username", "email", "is_active", "is_staff", "is_superuser", "created_at", "updated_at"
    )


@router.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }


@router.put("/users/{user_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(login_required)])
async def update_user(
    user_id: int,
    username: str = None,
    email: str = None,
    password: str = None,
    is_active: bool = None,
    is_staff: bool = None,
    is_superuser: bool = None
):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if username:
        user.username = username
    if email:
        user.email = email
    if password:
        user.password = pwd_context.hash(password)
    if is_active is not None:
        user.is_active = is_active
    if is_staff is not None:
        user.is_staff = is_staff
    if is_superuser is not None:
        user.is_superuser = is_superuser

    await user.save()
    return {"detail": "User updated successfully"}


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(superuser_required)])
async def delete_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"detail": "User deleted successfully"}




