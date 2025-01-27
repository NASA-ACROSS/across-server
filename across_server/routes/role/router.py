import uuid
from typing import Annotated, List

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
async def get_current_user():
    return db.models.User(id="173e35fa-9544-49e8-b5b9-d04ea884defb")


@router.get(
    "/",
    summary="Read roles",
    description="Read many roles.",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.Role],
    responses={
        status.HTTP_200_OK: {
            "model": List[schemas.Role],
            "description": "A list of roles",
        },
    },
)
async def get_many(service: Annotated[RoleService, Depends(RoleService)]):
    return await service.get_many()


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
):
    return await service.get(role_id)


@router.post(
    "/", dependencies=[Security(auth.strategies.global_access, scopes=["all:write"])]
)
async def create(
    service: Annotated[RoleService, Depends(RoleService)],
    data: schemas.RoleCreate,
):
    return status.HTTP_200_OK
