TORTOISE_ORM = {
    "connections": {
        "default": "mysql://root:root@localhost:3306/mydb"
    },
    "apps": {
        "models": {
            "models": ["applications.user.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
