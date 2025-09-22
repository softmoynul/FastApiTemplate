from fastapi import APIRouter
from applications.user.models import User
routes = APIRouter(
    prefix="/user", 
    tags=["Users"],
    # title="User API",
    # description="This is the User-related API",
    # version="1.0.0",
    # docs_url="/docs",       
    # redoc_url="/redoc",
    # openapi_url="/openapi.json"
)

@routes.post("/users")
async def create_user(
    username: str, 
    email: str, 
    phone_number: str, 
    password:str,
):
    user = await User.create(username=username, email=email, phone_number=phone_number, password=password)
    return user