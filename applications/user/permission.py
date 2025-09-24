from fastapi import APIRouter, HTTPException, status, Depends, Form
from applications.user.models import User, Permission, Group
from app.auth import *

permission = APIRouter()

# Create Group -> superuser only
@permission.post("/groups", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def create_group(
    name: str = Form(..., description="Group name"),
):
    if await Group.filter(name=name).exists():
        raise HTTPException(status_code=400, detail="Group already exists")
    group = await Group.create(name=name)
    return {"message": f"Group '{group.name}' created", "id": group.id}


# List Groups -> staff + superuser
@permission.get("/groups", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def list_groups():
    groups = await Group.all().values("id", "name")
    return groups


# Assign permissions to group -> superuser only
@permission.post("/groups/{group_id}/permissions", dependencies=[
        Depends(login_required),
        # Depends(staff_required),
        # Depends(permission_required("view_user")),
    ]
)
async def assign_permissions_to_group(
    group_id: int,
    permission_ids: list[int] = Form(..., description="List of permission IDs"),
):
    group = await Group.get_or_none(id=group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    permissions = await Permission.filter(id__in=permission_ids)
    if not permissions:
        raise HTTPException(status_code=404, detail="No valid permissions found")

    await group.permissions.add(*permissions)
    return {"message": f"Permissions assigned to group '{group.name}'"}


# Create Permission -> superuser only
@permission.post("/permissions", dependencies=[
        Depends(superuser_required),
        # Depends(staff_required),
    ]
)
async def create_permission(
    name: str = Form(..., description="Permission name (e.g. Can edit items)"),
    codename: str = Form(..., description="Unique codename (e.g. edit_item)"),
):
    if await Permission.filter(codename=codename).exists():
        raise HTTPException(
            status_code=400,
            detail=f"Permission with codename '{codename}' already exists"
        )

    permission = await Permission.create(name=name, codename=codename)
    return {
        "message": f"Permission '{permission.name}' created",
        "id": permission.id,
        "codename": permission.codename,
    }


@permission.get("/permissions", dependencies=[
        Depends(login_required),
        Depends(superuser_required),
    ]
)
async def list_permissions():
    return await Permission.all().values("id", "name", "codename")

