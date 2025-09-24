from fastapi import Request, HTTPException, status
from functools import wraps
from typing import Callable, Any
from applications.user.models import User
from .token import get_current_user

def login_required(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Any:
        current_user: User = await get_current_user(request)
        if not current_user or not current_user.is_active:
            raise HTTPException(status_code=401, detail="Authentication required")
        return await func(request, *args, current_user=current_user, **kwargs)
    return wrapper


def staff_required(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Any:
        current_user: User = await get_current_user(request)
        if not current_user.is_active:
            raise HTTPException(status_code=401, detail="Authentication required")
        if not current_user.is_staff and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Staff access required")
        return await func(request, *args, current_user=current_user, **kwargs)
    return wrapper


def superuser_required(func: Callable):
    @wraps(func)
    async def wrapper(request: Request, *args, **kwargs) -> Any:
        current_user: User = await get_current_user(request)
        if not current_user.is_active:
            raise HTTPException(status_code=401, detail="Authentication required")
        if not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Superuser access required")
        return await func(request, *args, current_user=current_user, **kwargs)
    return wrapper


def permission_required(permission_codename: str):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs) -> Any:
            current_user: User = await get_current_user(request)
            if not await current_user.has_permission(permission_codename):
                raise HTTPException(status_code=403, detail=f"Missing permission: {permission_codename}")
            return await func(request, *args, current_user=current_user, **kwargs)
        return wrapper
    return decorator
