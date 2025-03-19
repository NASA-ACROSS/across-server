from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import get_session, models


class PermissionService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(
        self, permission_ids: list[UUID] | None = None
    ) -> list[models.Permission]:
        # Limit to "group:" prefix permissions
        query = select(models.Permission).where(
            models.Permission.name.startswith("group")
        )

        # Get permissions by id
        if permission_ids:
            query = query.where(models.Permission.id.in_(permission_ids))

        permissions_result = await self.db.execute(query)
        permissions = list(permissions_result.scalars().all())
        return permissions
