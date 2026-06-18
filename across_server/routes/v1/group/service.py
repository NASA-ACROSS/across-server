from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import get_session, models
from .exceptions import GroupNotFoundException
from .role.service import GroupRoleService


class GroupService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
        group_role_service: Annotated[GroupRoleService, Depends(GroupRoleService)],
    ) -> None:
        self.db = db
        self.group_role_service = group_role_service

    async def get_many(self) -> Sequence[models.Group]:
        result = await self.db.scalars(select(models.Group))

        return result.all()

    async def get(self, id: UUID) -> models.Group:
        group = await self.db.get(models.Group, id)

        if group is None:
            raise GroupNotFoundException(id)

        await group.awaitable_attrs.users
        await group.awaitable_attrs.roles

        for group_role in group.roles:
            await group_role.awaitable_attrs.users

        return group

    async def remove_user(self, user: models.User, group_id: UUID) -> None:
        group = await self.get(id=group_id)

        # application layer removal of group roles from the user and service account
        # can be removed/refactored when across-server issue #196 is implemented
        for role in group.roles:
            if role in user.group_roles:
                await self.group_role_service.remove(role, user, group)

        if user in group.users:
            group.users.remove(user)

        await self.db.commit()
