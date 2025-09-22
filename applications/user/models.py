from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=50)
    password = fields.CharField(max_length=500)
    email = fields.CharField(max_length=100, unique=True)

    class Meta:
        table = "users"

    def __str__(self):
        return self.name
