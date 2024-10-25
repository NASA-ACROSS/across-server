from uuid import UUID

from typing import Annotated, Sequence
from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session, models

from .exceptions import GroupNotFoundException


class GroupService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(self) -> Sequence[models.Group]:
        result = await self.db.scalars(select(models.Group))

        return result.all()

    async def get(self, id: UUID) -> models.Group:
        record = await self.db.get(models.Group, id)

        if record is None:
            raise GroupNotFoundException(id)

        return record
