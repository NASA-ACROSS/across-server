from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....core.exceptions import DuplicateEntityException
from ....db import models
from ....db.database import get_session
from .exceptions import GroupInviteNotFoundException


class GroupInviteService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(self, group_id: UUID) -> list[models.GroupInvite]:
        result = await self.db.scalars(
            select(models.GroupInvite).where(models.GroupInvite.group_id == group_id)
        )

        invites = list(result.all())
        return invites

    async def get(self, id: UUID, group_id: UUID) -> models.GroupInvite:
        result = await self.db.scalars(
            select(models.GroupInvite)
            .where(models.GroupInvite.id == id)
            .where(models.GroupInvite.group_id == group_id)
        )

        invite = result.one_or_none()

        if invite is None:
            raise GroupInviteNotFoundException(id)

        return invite

    async def send(
        self, sender_id: UUID, group: models.Group, receiver: models.User
    ) -> models.GroupInvite:
        """Invite a user to a group by sending them an email and creating an invite entity record in the database"""
        # Don't invite user if they're already in the group
        if receiver in group.users:
            raise DuplicateEntityException("User", "receiver_email", receiver.email)

        # Don't invite user if they've already been invited
        invites = await self.get_many(group.id)
        if receiver.email in [invite.receiver_email for invite in invites]:
            raise DuplicateEntityException(
                "UserInvite", "receiver_email", receiver.email
            )

        invite = models.GroupInvite(
            sender_id=sender_id,
            group_id=group.id,
            receiver_email=receiver.email,
            receiver_id=receiver.id,
        )

        self.db.add(invite)
        await self.db.commit()
        await self.db.refresh(invite)

        return invite

    async def accept(self, invite: models.GroupInvite) -> None:
        """Accept a group invite and delete the invite entity"""
        invite.group.users.append(invite.receiver)
        await self.db.delete(invite)
        await self.db.commit()

    async def delete(self, invite: models.GroupInvite) -> None:
        """Delete an invite entity from the database"""
        await self.db.delete(invite)
        await self.db.commit()
