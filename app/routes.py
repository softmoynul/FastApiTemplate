from fastapi import FastAPI, APIRouter

def create_sub_app(name: str, router: APIRouter):
    app = FastAPI(
        title=f"{name.capitalize()} API",
        description=f"This is the {name.capitalize()} API",
        version="1.0.0",
        docs_url="/docs",      
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    app.include_router(router)
    return app
