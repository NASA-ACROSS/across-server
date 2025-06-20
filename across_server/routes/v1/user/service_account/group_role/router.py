from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status

from across_server import auth

from ....group.role.service import GroupRoleService
from ...service import UserService
from .. import schemas
from ..service import ServiceAccountService
from .service import ServiceAccountGroupRoleService

router = APIRouter(
    prefix="/user/{user_id}/service-account/{service_account_id}/group-role",
    tags=["ServiceAccount"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The service account, user, or group role does not exist.",
        },
    },
)


@router.post(
    "/{group_role_id}",
    summary="Assign group role",
    description="Assign a group role to a service account.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "Group Role has been assigned to service account",
        },
    },
)
async def assign(
    service: Annotated[
        ServiceAccountGroupRoleService, Depends(ServiceAccountGroupRoleService)
    ],
    auth_user: Annotated[auth.schemas.AuthUser, Security(auth.strategies.self_access)],
    service_account_id: UUID,
    group_role_id: UUID,
    service_account_service: Annotated[
        ServiceAccountService, Depends(ServiceAccountService)
    ],
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    user_service: Annotated[UserService, Depends(UserService)],
) -> schemas.ServiceAccount:
    user = await user_service.get(auth_user.id)
    service_account = await service_account_service.get(
        service_account_id=service_account_id, user_id=auth_user.id
    )
    group_role = await group_role_service.get_for_user(group_role_id, auth_user.id)

    role_assigned_account = await service.assign(service_account, group_role, user)
    return schemas.ServiceAccount.model_validate(role_assigned_account)


@router.delete(
    "/{group_role_id}",
    summary="Remove group role",
    description="Remove a group role from a service account.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "Group Role has been removed from the service account",
        },
    },
)
async def remove(
    service: Annotated[
        ServiceAccountGroupRoleService, Depends(ServiceAccountGroupRoleService)
    ],
    auth_user: Annotated[auth.schemas.AuthUser, Security(auth.strategies.self_access)],
    service_account_id: UUID,
    group_role_id: UUID,
    service_account_service: Annotated[
        ServiceAccountService, Depends(ServiceAccountService)
    ],
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
) -> schemas.ServiceAccount:
    service_account = await service_account_service.get(
        service_account_id=service_account_id, user_id=auth_user.id
    )
    group_role = await group_role_service.get_for_user(group_role_id, auth_user.id)

    role_removed_account = await service.remove(service_account, group_role)
    return schemas.ServiceAccount.model_validate(role_removed_account)
