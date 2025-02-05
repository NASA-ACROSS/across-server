from fastapi import FastAPI, status

from . import auth
from .core.config import config
from .routes import group, observation, role, user

app = FastAPI(
    title="ACROSS Server",
    summary="Astrophysics Cross-Observatory Science Support (ACROSS)",
    description="Server providing tools and utilities for various NASA missions to aid in coordination of large observation efforts.",
    root_path=config.ROOT_PATH,
)


@app.get(
    "/",
    summary="Health Check",
    description="Container Health Check Route",
    status_code=status.HTTP_200_OK,
)
async def get():
    return "ok"


app.include_router(auth.router)
app.include_router(user.router)
app.include_router(user.service_account.router)
app.include_router(role.router)
app.include_router(group.router)
app.include_router(group.group_role.router)
app.include_router(observation.router)
