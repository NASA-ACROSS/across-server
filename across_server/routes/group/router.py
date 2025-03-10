import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Security, status

from ...auth.strategies import global_access, group_access
from ...db import models
from . import schemas
from .service import GroupService

router = APIRouter(
    prefix="/group",
    tags=["Group"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The group does not exist.",
        },
    },
)


# replace with security stuff
async def get_current_user():
    return models.User(id="173e35fa-9544-49e8-b5b9-d04ea884defb")


@router.get(
    "/",
    summary="Read groups",
    description="Read many groups.",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.Group],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Group],
            "description": "A list of groups",
        },
    },
    dependencies=[Security(global_access, scopes=["group:read"])],
)
async def get_many(
    service: Annotated[GroupService, Depends(GroupService)],
):
    return await service.get_many()


@router.get(
    "/{group_id}",
    summary="Read a group",
    description="Read a group by role ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Group,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Group,
            "description": "The requested group",
        },
    },
    dependencies=[Security(group_access, scopes=["group:read"])],
)
async def get(
    service: Annotated[GroupService, Depends(GroupService)],
    group_id: Annotated[uuid.UUID, Path(title="UUID of the group")],
):
    return await service.get(group_id)
