from tortoise import fields
from tortoise.models import Model

class Permission(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    codename = fields.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"{self.codename}"


class Group(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)

    permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission", related_name="groups", through="group_permissions"
    )

    def __str__(self):
        return self.name

class User(Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=100, unique=True)
    username = fields.CharField(max_length=50, unique=True)
    password = fields.CharField(max_length=128)
    is_active = fields.BooleanField(default=True)
    is_staff = fields.BooleanField(default=False)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    groups: fields.ManyToManyRelation["Group"] = fields.ManyToManyField(
        "models.Group", related_name="users", through="user_groups"
    )

    user_permissions: fields.ManyToManyRelation["Permission"] = fields.ManyToManyField(
        "models.Permission", related_name="users", through="user_permissions"
    )
    
    async def has_permission(self, codename: str) -> bool:
        if self.is_superuser:
            return True

        if await self.user_permissions.filter(codename=codename).exists():
            return True

        if await Permission.filter(
            codename=codename,
            groups__in=await self.groups.all()
        ).exists():
            return True

        return False

    class Meta:
        table = "users"

    def __str__(self):
        return f"{self.username} ({self.email})"
    
