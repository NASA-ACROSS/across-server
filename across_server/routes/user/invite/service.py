from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import models
from ....db.database import get_session
from ....routes.group.invite.exceptions import GroupInviteNotFoundException


class UserInviteService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(self, user_id: UUID, invite_id: UUID) -> models.GroupInvite:
        result = await self.db.scalars(
            select(models.GroupInvite)
            .where(models.GroupInvite.receiver_id == user_id)
            .where(models.GroupInvite.id == invite_id)
        )

        invite = result.one_or_none()
        if invite is None:
            raise GroupInviteNotFoundException(invite_id)

        return invite

    async def get_many(self, user_id: UUID) -> list[models.GroupInvite]:
        result = await self.db.scalars(
            select(models.GroupInvite).where(models.GroupInvite.receiver_id == user_id)
        )

        invites = list(result.all())
        return invites
