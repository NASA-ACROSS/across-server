import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Security, status

from ...auth.strategies import global_access, group_access
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
) -> list[schemas.Group]:
    group_models = await service.get_many()
    return [schemas.Group.model_validate(group) for group in group_models]



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
) -> schemas.Group:
    group_model = await service.get(group_id)
    return schemas.Group.model_validate(group_model)

