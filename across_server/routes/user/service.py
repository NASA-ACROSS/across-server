from uuid import UUID

from typing import Annotated, Sequence
from fastapi import Depends
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from . import schemas

from ...db import models
from ...db.database import get_session
from .exceptions import DuplicateUserException, UserNotFoundException


class UserService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get_many(self) -> Sequence[models.User]:
        result = await self.db.scalars(select(models.User))
        users = result.all()

        return users

    async def get(self, user_id: UUID) -> models.User:
        user = await self.db.get(models.User, user_id)

        if user is None:
            raise UserNotFoundException(user_id)

        return user

    async def exists(
        self,
        user_id: UUID | None = None,
        email: EmailStr | None = None,
    ) -> bool:
        if not user_id and not email:
            raise ValueError("Provide either a user_id or an email.")

        query = select(models.User).where(
            (models.User.id == user_id) | (models.User.email == email)
        )

        result = await self.db.execute(query)
        user = result.scalar_one_or_none()

        return bool(user)

    async def create(self, data: schemas.UserCreate) -> models.User:
        exists = await self.exists(email=data.email)

        if exists:
            raise DuplicateUserException(field_name="email", field_value=data.email)

        user = models.User(**data.model_dump(exclude_unset=True))

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update(
        self,
        user_id: UUID,
        data: schemas.UserUpdate,
        modified_by: models.User,
    ) -> models.User:
        user = await self.get(user_id)

        values = data.model_dump(exclude_unset=True).items()

        for key, value in values:
            setattr(user, key, value)

        user.modified_by_id = modified_by.id

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def delete(self, user_id: UUID) -> models.User:
        user = await self.get(user_id)

        await self.db.delete(user)
        await self.db.commit()

        return user
