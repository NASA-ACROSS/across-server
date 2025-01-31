import datetime
import hashlib
from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth.config import auth_config
from ....core import config
from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import ServiceAccountNotFoundException


class ServiceAccountService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    @staticmethod
    def generate_secret_key() -> str:
        now = datetime.datetime.now()

        # Get timestamp in seconds
        timestamp_seconds = now.replace(tzinfo=datetime.timezone.utc).timestamp()

        # Convert to nanoseconds
        timestamp_nanoseconds = int(timestamp_seconds * 1e9)

        secret_string = auth_config.SERVICE_ACCOUNT_SECRET_KEY + str(
            timestamp_nanoseconds
        )

        return hashlib.sha512(secret_string.encode()).hexdigest()

    async def get(
        self, service_account_id: UUID, user_id: UUID
    ) -> models.ServiceAccount:
        query = select(models.ServiceAccount).where(
            models.ServiceAccount.id == service_account_id,
            models.ServiceAccount.user_id == user_id,
        )

        result = await self.db.execute(query)
        service_account = result.scalar_one_or_none()

        if service_account is None:
            raise ServiceAccountNotFoundException(service_account_id)

        return service_account

    async def get_many(self, user_id: UUID) -> Sequence[models.ServiceAccount]:
        result = await self.db.scalars(
            select(models.ServiceAccount).filter(
                models.ServiceAccount.user_id == user_id
            )
        )
        service_accounts = result.all()

        return service_accounts

    async def create(
        self, service_account_create: schemas.ServiceAccountCreate, created_by_id: UUID
    ) -> models.ServiceAccount:
        service_account_create.expiration_duration = (
            service_account_create.expiration_duration
            if service_account_create.expiration_duration
            else config.SERVICE_ACCOUNT_EXPIRATION_DURATION
        )

        expiration = datetime.datetime.now() + datetime.timedelta(
            days=service_account_create.expiration_duration
        )

        service_account = models.ServiceAccount(
            user_id=created_by_id,
            name=service_account_create.name,
            description=service_account_create.description,
            secret_key=self.generate_secret_key(),
            expiration_duration=service_account_create.expiration_duration,
            expiration=expiration,
            created_by_id=created_by_id,
        )

        self.db.add(service_account)
        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def update(
        self,
        id: UUID,
        service_account_update: schemas.ServiceAccountUpdate,
        modified_by_id: UUID,
    ) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id, user_id=modified_by_id)

        values = service_account_update.model_dump(exclude_unset=True).items()

        for key, value in values:
            setattr(service_account, key, value)

        if service_account_update.expiration_duration:
            service_account.expiration = datetime.datetime.now() + datetime.timedelta(
                days=service_account_update.expiration_duration
            )
            service_account.expiration_duration = (
                service_account_update.expiration_duration
            )

        service_account.modified_by_id = modified_by_id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def rotate_key(self, id: UUID, modified_by_id: UUID) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id, user_id=modified_by_id)

        service_account.secret_key = self.generate_secret_key()
        service_account.expiration = datetime.datetime.now() + datetime.timedelta(
            days=service_account.expiration_duration
        )

        service_account.modified_by_id = modified_by_id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def expire_key(self, id: UUID, modified_by_id: UUID) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id, user_id=modified_by_id)

        service_account.expiration = datetime.datetime.now()
        service_account.modified_by_id = modified_by_id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account
