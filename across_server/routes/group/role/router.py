import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from ....auth.strategies import group_access
from ...permission.service import PermissionService
from ...user.service import UserService
from ..service import GroupService
from . import schemas
from .service import GroupRoleService

router = APIRouter(
    prefix="/group/{group_id}",
    tags=["Group Role"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The group or role does not exist.",
        },
    },
)


@router.get(
    "/role",
    summary="Read group roles",
    description="Read many group roles.",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.GroupRoleRead],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.GroupRoleRead],
            "description": "A list of group roles",
        },
    },
    dependencies=[Security(group_access)],
)
async def get_many(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    group_id: uuid.UUID,
) -> list[schemas.GroupRoleRead]:
    group_roles = await group_role_service.get_many(group_id)
    return [
        schemas.GroupRoleRead.model_validate(group_role) for group_role in group_roles
    ]


@router.get(
    "/role/{group_role_id}",
    summary="Read a group role",
    description="Read a group role by role ID.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.GroupRole,
            "description": "The requested group role",
        },
    },
    dependencies=[Security(group_access)],
)
async def get(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    group_id: uuid.UUID,
    group_role_id: uuid.UUID,
) -> schemas.GroupRoleRead:
    group_role = await group_role_service.get_for_group(group_role_id, group_id)
    return schemas.GroupRoleRead.model_validate(group_role)


@router.put(
    "/user/{user_id}/role/{group_role_id}",
    summary="Assign a group role to a user",
    description="Assign a group role by id to a user id within that group.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Group role successfully assigned to user",
        },
    },
    dependencies=[Security(group_access, scopes=["group:user:write"])],
)
async def assign(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    user_service: Annotated[UserService, Depends(UserService)],
    group_service: Annotated[GroupService, Depends(GroupService)],
    group_role_id: uuid.UUID,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    user = await user_service.get(user_id)
    group = await group_service.get(group_id)
    group_role = await group_role_service.get_for_group(group_role_id, group_id)
    await group_role_service.assign(group_role, user, group)


@router.delete(
    "/user/{user_id}/role/{group_role_id}",
    summary="Remove a group role from a user",
    description="Remove a group role by id from a user id within that group.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Group role successfully removed from user",
        },
    },
    dependencies=[Security(group_access, scopes=["group:user:write"])],
)
async def remove(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    user_service: Annotated[UserService, Depends(UserService)],
    group_service: Annotated[GroupService, Depends(GroupService)],
    group_role_id: uuid.UUID,
    group_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    user = await user_service.get(user_id)
    group = await group_service.get(group_id)
    group_role = await group_role_service.get_for_group(group_role_id, group_id)
    await group_role_service.remove(group_role, user, group)


@router.post(
    "/role",
    summary="Create a group role",
    description="Create a group role with a set of permissions in a group that you control",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.GroupRoleRead,
            "description": "The created group role",
        },
    },
    dependencies=[Security(group_access, scopes=["group:role:write"])],
)
async def create(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    permission_service: Annotated[PermissionService, Depends(PermissionService)],
    data: schemas.GroupRoleCreate,
    group_id: uuid.UUID,
) -> schemas.GroupRoleRead:
    permissions = await permission_service.get_many(data.permission_ids)
    created_role = await group_role_service.create(
        role_name=data.name, permissions=permissions, group_id=group_id
    )
    return schemas.GroupRoleRead.model_validate(created_role)


@router.put(
    "/role/{group_role_id}",
    summary="Update a group role",
    description="Update a group role and its permissions in a group that you control",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.GroupRoleCreate,
            "description": "The updated group role",
        },
    },
    dependencies=[Security(group_access, scopes=["group:role:write"])],
)
async def update_role(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    group_service: Annotated[GroupService, Depends(GroupService)],
    permission_service: Annotated[PermissionService, Depends(PermissionService)],
    data: schemas.GroupRoleCreate,
    group_role_id: uuid.UUID,
    group_id: uuid.UUID,
) -> schemas.GroupRoleRead:
    group = await group_service.get(group_id)
    group_role = await group_role_service.get_for_group(group_role_id, group_id)
    permissions = await permission_service.get_many(data.permission_ids)

    updated_role = await group_role_service.update(
        permissions=permissions, role_name=data.name, group_role=group_role, group=group
    )
    return schemas.GroupRoleRead.model_validate(updated_role)


@router.delete(
    "/role/{group_role_id}",
    summary="Delete a group role",
    description="Delete a group role by role ID.",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "model": None,
            "description": "Group role successfully deleted",
        },
    },
    dependencies=[Security(group_access, scopes=["group:role:write"])],
)
async def delete(
    group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    group_id: uuid.UUID,
    group_role_id: uuid.UUID,
) -> None:
    group_role = await group_role_service.get_for_group(group_role_id, group_id)
    await group_role_service.delete(group_role)
