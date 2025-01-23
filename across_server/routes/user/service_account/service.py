import datetime
import hashlib
from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.auth.config import auth_config

from ....db import models
from ....db.database import get_session
from .exceptions import ServiceAccountNotFoundException
from .schemas import ServiceAccountCreate, ServiceAccountUpdate


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
        timestamp_seconds = now.timestamp()

        # Convert to nanoseconds
        timestamp_nanoseconds = int(timestamp_seconds * 1e9)

        secret_string = auth_config.SERVICE_ACCOUNT_SECRET_KEY + str(
            timestamp_nanoseconds
        )

        return hashlib.sha512(secret_string.encode()).hexdigest()

    async def get(self, service_account_id: UUID) -> models.ServiceAccount:
        query = select(models.ServiceAccount).where(
            models.ServiceAccount.id == service_account_id
        )

        result = await self.db.execute(query)
        service_account = result.scalar_one_or_none()

        if service_account is None:
            raise ServiceAccountNotFoundException(service_account_id)

        return service_account

    async def get_many(self) -> Sequence[models.ServiceAccount]:
        result = await self.db.scalars(select(models.ServiceAccount))
        service_accounts = result.all()

        return service_accounts

    async def create(
        self, serviceAccount: ServiceAccountCreate, created_by: models.User
    ) -> models.ServiceAccount:
        if not serviceAccount.expiration_duration:
            serviceAccount.expiration_duration = 30

        expiration = datetime.datetime.now() + datetime.timedelta(
            days=serviceAccount.expiration_duration
        )

        service_account = models.ServiceAccount(
            user_id=created_by.id,
            name=serviceAccount.name,
            description=serviceAccount.description,
            secret_key=self.generate_secret_key(),
            expiration_duration=serviceAccount.expiration_duration,
            expiration=expiration,
        )

        self.db.add(service_account)
        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def update(
        self, id: UUID, serviceAccount: ServiceAccountUpdate, modified_by: models.User
    ) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id)

        if serviceAccount.name:
            service_account.name = serviceAccount.name
        if serviceAccount.description:
            service_account.description = serviceAccount.description
        if serviceAccount.expiration_duration:
            service_account.expiration = datetime.datetime.now() + datetime.timedelta(
                days=serviceAccount.expiration_duration
            )

        service_account.modified_by_id = modified_by.id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def rotate_key(
        self, id: UUID, modified_by: models.User
    ) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id)

        service_account.secret_key = self.generate_secret_key()

        service_account.modified_by_id = modified_by.id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    async def expire_key(
        self, id: UUID, modified_by: models.User
    ) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id)

        service_account.expiration = datetime.datetime.now()
        service_account.modified_by_id = modified_by.id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account
