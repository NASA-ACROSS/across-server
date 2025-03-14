import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from ... import auth, db
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


# replace with security stuff
async def get_current_user() -> db.models.User:
    return db.models.User(id="173e35fa-9544-49e8-b5b9-d04ea884defb")


@router.get(
    "/",
    summary="Read roles",
    description="Read many roles.",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.Role],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Role],
            "description": "A list of roles",
        },
    },
)
async def get_many(
    service: Annotated[RoleService, Depends(RoleService)],
) -> list[schemas.Role]:
    many_role_models = await service.get_many()
    return [schemas.Role.model_validate(role_model) for role_model in many_role_models]


@router.get(
    "/{role_id}",
    summary="Read a role",
    description="Read a role by role ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Role,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Role,
            "description": "The requested role",
        },
    },
)
async def get(
    service: Annotated[RoleService, Depends(RoleService)], role_id: uuid.UUID
) -> schemas.Role:
    role_model = await service.get(role_id)
    return schemas.Role.model_validate(role_model)


@router.post("/", dependencies=[Security(auth.global_access, scopes=["all:write"])])
async def create(
    service: Annotated[RoleService, Depends(RoleService)],
    data: schemas.RoleCreate,
) -> int:
    return status.HTTP_200_OK
