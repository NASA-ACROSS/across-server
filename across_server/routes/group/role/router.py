import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from . import schemas
from .service import GroupRoleService

router = APIRouter(
    prefix="/group/{group_id}/role",
    tags=["Group Role"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The group role does not exist.",
        },
    },
)


@router.get(
    "/",
    summary="Read group roles",
    description="Read many group roles.",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.GroupRole],
    responses={
        status.HTTP_200_OK: {
            "model": List[schemas.GroupRole],
            "description": "A list of group roles",
        },
    },
)
async def get_many(service: Annotated[GroupRoleService, Depends(GroupRoleService)]):
    return await service.get_many()


@router.get(
    "/{group_role_id}",
    summary="Read a group role",
    description="Read a group role by role ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.GroupRole,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.GroupRole,
            "description": "The requested group role",
        },
    },
)
async def get(
    service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    group_role_id: uuid.UUID,
):
    return await service.get(group_role_id)
