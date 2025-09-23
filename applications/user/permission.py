from fastapi import APIRouter, HTTPException, status, Depends, Form
from applications.user.models import User, Permission, Group
from app.token import superuser_required, staff_required

permission = APIRouter()

# Create Group -> superuser only
@permission.post("/groups", status_code=status.HTTP_201_CREATED)
async def create_group(
    name: str = Form(..., description="Group name"),
    current_user=Depends(superuser_required)
):
    if await Group.filter(name=name).exists():
        raise HTTPException(status_code=400, detail="Group already exists")
    group = await Group.create(name=name)
    return {"message": f"Group '{group.name}' created", "id": group.id}


# List Groups -> staff + superuser
@permission.get("/groups", status_code=status.HTTP_200_OK)
async def list_groups(current_user: User = Depends(staff_required)):
    groups = await Group.all().values("id", "name")
    return groups


# Assign permissions to group -> superuser only
@permission.post("/groups/{group_id}/permissions")
async def assign_permissions_to_group(
    group_id: int,
    permission_ids: list[int] = Form(..., description="List of permission IDs"),
    current_user=Depends(superuser_required)
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
@permission.post("/permissions", status_code=status.HTTP_201_CREATED)
async def create_permission(
    name: str = Form(..., description="Permission name"),
    codename: str = Form(..., description="Unique codename"),
    current_user=Depends(superuser_required)
):
    if await Permission.filter(codename=codename).exists():
        raise HTTPException(status_code=400, detail="Permission codename already exists")

    permission = await Permission.create(name=name, codename=codename)
    return {"message": f"Permission '{permission.name}' created", "id": permission.id}


# List Permissions -> staff + superuser
@permission.get("/permissions")
async def list_permissions(current_user=Depends(staff_required)):
    return await Permission.all().values("id", "name", "codename")

