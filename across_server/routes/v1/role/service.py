from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import get_session, models
from .exceptions import RoleNotFoundException


class RoleService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(self) -> Sequence[models.Role]:
        result = await self.db.scalars(select(models.Role))
        roles = result.all()

        return roles

    async def get(self, role_id: UUID) -> models.Role:
        role = await self.db.get(models.Role, role_id)

        if role is None:
            raise RoleNotFoundException(role_id)

        return role
