import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Security, status

from ....auth.strategies import global_access, group_access
from ..user.service import UserService
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
    operation_id="get_groups",
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
    operation_id="get_group",
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


@router.delete(
    "/{group_id}/user/{user_id}",
    summary="Remove a user from a group",
    description="Remove a user from a group by ID",
    operation_id="remove_user",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Security(group_access, scopes=["group:user:write"])],
)
async def remove_user(
    user_service: Annotated[UserService, Depends(UserService)],
    group_service: Annotated[GroupService, Depends(GroupService)],
    user_id: uuid.UUID,
    group_id: uuid.UUID,
) -> None:
    user = await user_service.get(user_id)
    await group_service.remove_user(user, group_id)
