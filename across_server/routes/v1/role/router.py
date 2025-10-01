import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from ....util.decorators import local_only_route
from . import schemas
from .service import RoleService

router = APIRouter(
    prefix="/role",
    tags=["Role"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The role does not exist.",
        },
    },
)


@local_only_route(
    router,
    path="/",
    methods=["GET"],
    summary="Read roles",
    description="Read many roles",
)
async def get_many(
    service: Annotated[RoleService, Depends(RoleService)],
) -> list[schemas.Role]:
    many_role_models = await service.get_many()
    return [schemas.Role.model_validate(role_model) for role_model in many_role_models]


@local_only_route(
    router,
    path="/{role_id}",
    methods=["GET"],
    summary="Read a role",
    description="Read a role by role ID.",
)
async def get(
    service: Annotated[RoleService, Depends(RoleService)], role_id: uuid.UUID
) -> schemas.Role:
    role_model = await service.get(role_id)
    return schemas.Role.model_validate(role_model)
