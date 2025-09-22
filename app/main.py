from fastapi import FastAPI, HTTPException, UploadFile, Form
from typing import Optional
from tortoise.contrib.fastapi import register_tortoise
from .routes import create_sub_app

import importlib
app = FastAPI()
apps = ["user", "item", "auth"]


register_tortoise(
    app,
    db_url="mysql://root:root@localhost:3306/mydb",
    modules={"models": ["applications.user.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

for app_name in apps:
    routes_module = importlib.import_module(f"applications.{app_name}.routes")
    sub_app = create_sub_app(app_name, routes_module.router)
    app.mount(f"/{app_name}", sub_app)