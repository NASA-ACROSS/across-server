from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import get_session, models


class PermissionService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_all(
        self,
    ) -> list[models.Permission]:
        # Limit to "group:" prefix permissions
        query = select(models.Permission).where(
            models.Permission.name.startswith("group")
        )

        permissions_result = await self.db.execute(query)
        permissions = list(permissions_result.scalars().all())
        return permissions

    async def get_many(self, permission_ids: list[UUID]) -> list[models.Permission]:
        # Limit to "group:" prefix permissions
        query = (
            select(models.Permission)
            .where(models.Permission.name.startswith("group"))
            .where(models.Permission.id.in_(permission_ids))
        )

        permissions_result = await self.db.execute(query)
        permissions = list(permissions_result.scalars().all())
        return permissions
