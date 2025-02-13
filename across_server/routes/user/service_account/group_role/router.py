from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Security, status

from across_server import auth

from .. import schemas
from .service import ServiceAccountGroupRoleService

router = APIRouter(
    prefix="/user/{user_id}/service-account/{service_account_id}/group-role",
    tags=["ServiceAccount"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The service account does not exist.",
        },
    },
)


@router.post(
    "/{group_role_id}",
    summary="Assign group role",
    description="Assign a group role to a service account.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.ServiceAccount,
            "description": "The newly created service account",
        },
    },
    dependencies=[
        Security(
            auth.strategies.global_access,
            scopes=["user:service_account:group:role:write"],
        )
    ],
)
async def assign(
    service: Annotated[
        ServiceAccountGroupRoleService, Depends(ServiceAccountGroupRoleService)
    ],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    service_account_id: Annotated[
        UUID, Path(title="UUID of the service account to assign to")
    ],
    group_role_id: Annotated[UUID, Path(title="UUID of the group role to assign")],
):
    service.assign(service_account_id, group_role_id, user_id=auth_user.id)
    return


@router.delete(
    "/{group_role_id}",
    summary="Remove group role",
    description="Remove a group role from a service account.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "The updated service account",
        },
    },
    dependencies=[
        Security(
            auth.strategies.global_access,
            scopes=["user:service_account:group:role:write"],
        ),
    ],
)
async def remove(
    service: Annotated[
        ServiceAccountGroupRoleService, Depends(ServiceAccountGroupRoleService)
    ],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    service_account_id: Annotated[
        UUID, Path(title="UUID of the service account to remove from")
    ],
    group_role_id: Annotated[UUID, Path(title="UUID of the group role to remove")],
):
    service.remove(service_account_id, group_role_id, user_id=auth_user.id)
    return
