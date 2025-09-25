from fastapi import APIRouter, HTTPException, status, Depends, Form, Query, Body
from typing import List, Optional
from app.auth import *
from applications.user.models import User, Permission, Group
from .permission import permission
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()
router.include_router(permission, tags=["Permission"])




# ------------------------------------------------------------------------
@router.post("/users", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def create_user(
    username: str = Form(..., description="Username"),
    email: str = Form(..., description="Email"),
    password: str = Form(..., min_length=8, description="User password", password=True, example="********"),
    is_active: bool = Form(True),
    is_staff: bool = Form(False),
    is_superuser: bool = Form(False),
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
        "new_user": new_user
    }


@router.get("/users", dependencies=[
        # Depends(login_required),
        Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def get_all_users():
    return await User.all().values(
        "id", "username", "email", "is_active", "is_staff", "is_superuser", "created_at", "updated_at"
    )


@router.get("/users/{user_id}", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def get_user(user_id: int):
    user = await User.get_or_none(id=user_id).prefetch_related("groups", "user_permissions")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # collect group names
    groups = [group.name for group in user.groups]

    # collect user permissions
    user_perms = [perm.codename for perm in user.user_permissions]

    # collect group permissions as well (if you want full perms including groups)
    group_perms = []
    for group in user.groups:
        perms = await group.permissions.all()
        group_perms.extend([perm.codename for perm in perms])

    # merge unique permissions
    all_perms = list(set(user_perms + group_perms))

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "groups": groups,
        "permissions": all_perms,
    }


@router.put("/users/{user_id}", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def update_user(
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    password: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_staff: Optional[bool] = None,
    is_superuser: Optional[bool] = None,
    group_ids: Optional[List[int]] = None,
    permission_ids: Optional[List[int]] = None
):
    user = await User.get_or_none(id=user_id).prefetch_related("groups", "user_permissions")
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

    if group_ids is not None:
        groups = await Group.filter(id__in=group_ids)
        await user.groups.clear()
        await user.groups.add(*groups)

    if permission_ids is not None:
        permissions = await Permission.filter(id__in=permission_ids)
        await user.user_permissions.clear()
        await user.user_permissions.add(*permissions)

    return {
        "detail": "User updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "groups": [g.id for g in await user.groups.all()],
            "permissions": [p.id for p in await user.user_permissions.all()],
        }
    }


@router.delete("/users/{user_id}", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def delete_user(user_id: int):
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await user.delete()
    return {"detail": "User deleted successfully"}

