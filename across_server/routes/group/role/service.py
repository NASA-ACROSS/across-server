from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import get_session, models
from ...group.exceptions import GroupNotFoundException
from .exceptions import GroupRoleNotFoundException


class GroupRoleService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(self, group_id: UUID) -> Sequence[models.GroupRole]:
        result = await self.db.scalars(
            select(models.GroupRole).where(models.GroupRole.group_id == group_id)
        )

        roles = result.all()
        return roles

    async def get_for_group(self, id: UUID, group_id: UUID) -> models.GroupRole:
        result = await self.db.scalars(
            select(models.GroupRole)
            .where(models.GroupRole.id == id)
            .where(models.GroupRole.group_id == group_id)
            .limit(1)
        )

        role = result.one_or_none()

        if role is None:
            raise GroupRoleNotFoundException(id)

        return role

    async def get_for_user(self, id: UUID, user_id: UUID) -> models.GroupRole:
        result = await self.db.scalars(
            select(models.GroupRole)
            .where(models.GroupRole.id == id)
            .where(models.GroupRole.users.any(models.User.id == user_id))
            .limit(1)
        )

        role = result.one_or_none()

        if role is None:
            raise GroupRoleNotFoundException(id)

        return role

    async def assign(
        self, group_role: models.GroupRole, user: models.User, group: models.Group
    ) -> models.GroupRole:
        # User must belong to group
        if group not in user.groups:
            raise GroupNotFoundException(group.id)

        # Group role must belong to group
        if group_role not in group.roles:
            raise GroupRoleNotFoundException(group_role.id)

        user.group_roles.append(group_role)

        await self.db.commit()
        return group_role

    async def remove(
        self, group_role: models.GroupRole, user: models.User, group: models.Group
    ) -> None:
        # User must belong to group
        if group not in user.groups:
            raise GroupNotFoundException(group.id)

        # Group role must belong to group
        if group_role not in group.roles:
            raise GroupRoleNotFoundException(group_role.id)

        # Remove the group role from all user service accounts
        for service_account in user.service_accounts:
            if group_role in service_account.group_roles:
                service_account.group_roles.remove(group_role)

        # Remove the group role from the user
        if group_role in user.group_roles:
            user.group_roles.remove(group_role)

        await self.db.commit()

    async def create(
        self, role_name: str, permissions: list[models.Permission], group_id: UUID
    ) -> models.GroupRole:
        group_role = models.GroupRole(
            group_id=group_id, name=role_name, permissions=permissions
        )

        self.db.add(group_role)

        await self.db.commit()
        return group_role

    async def update(
        self,
        role_name: str,
        permissions: list[models.Permission],
        group_role: models.GroupRole,
        group: models.Group,
    ) -> models.GroupRole:
        # Group role must belong to group
        if group_role not in group.roles:
            raise GroupRoleNotFoundException(group_role.id)

        group_role.name = role_name
        group_role.permissions = permissions

        await self.db.commit()
        return group_role

    async def delete(self, group_role: models.GroupRole) -> None:
        # Delete the role, this will cascade delete the group_role from all users and service accounts.
        await self.db.delete(group_role)

        await self.db.commit()
