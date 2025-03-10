from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import get_session, models
from .exceptions import GroupRoleNotFoundException


class GroupRoleService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(self) -> Sequence[models.GroupRole]:
        result = await self.db.scalars(select(models.GroupRole))
        roles = result.all()

        return roles

    async def get(self, id: UUID) -> models.GroupRole:
        role = await self.db.get(models.GroupRole, id)

        if role is None:
            raise GroupRoleNotFoundException(id)

        return role
