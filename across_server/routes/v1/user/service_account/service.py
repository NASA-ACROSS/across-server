import datetime
import secrets
from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from across_server import core

from .....auth.hashing import password_hasher
from .....auth.schemas import SecretKeySchema
from .....core import config
from .....db import models
from .....db.database import get_session
from . import schemas
from .exceptions import ServiceAccountNotFoundException


class ServiceAccountService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    @staticmethod
    def generate_secret_key(expiration_duration: int = 30) -> SecretKeySchema:
        """Generate a secret key for a service account which includes the expiration date of the key."""
        now = datetime.datetime.now()

        return SecretKeySchema(
            key=secrets.token_hex(64),
            expiration=now + datetime.timedelta(days=expiration_duration),
        )

    async def get(
        self, service_account_id: UUID, user_id: UUID
    ) -> models.ServiceAccount:
        query = (
            select(models.ServiceAccount)
            .join(models.ServiceAccount.user)
            .where(
                models.ServiceAccount.id == service_account_id,
                models.User.id == user_id,
            )
        )

        result = await self.db.execute(query)
        service_account = result.scalar_one_or_none()

        if service_account is None:
            raise ServiceAccountNotFoundException(service_account_id)

        return service_account

    async def get_many(self, user_id: UUID) -> Sequence[models.ServiceAccount]:
        result = await self.db.scalars(
            select(models.ServiceAccount)
            .join(models.ServiceAccount.user)
            .filter(models.User.id == user_id)
        )
        service_accounts = result.all()

        return service_accounts

    async def create(
        self, service_account_create: schemas.ServiceAccountCreate, created_by_id: UUID
    ) -> core.schemas.ServiceAccountSecret:
        service_account_create.expiration_duration = (
            service_account_create.expiration_duration
            if service_account_create.expiration_duration
            else config.SERVICE_ACCOUNT_EXPIRATION_DURATION
        )

        # generate a secret key for the service account that will be sent to the user
        secret_key_information = self.generate_secret_key(
            expiration_duration=service_account_create.expiration_duration
        )

        # hash the secret key for storage in database
        hashed_secret_key = password_hasher.hash(secret_key_information.key)

        user_query = select(models.User).where(
            models.User.id == created_by_id,
        )

        res = await self.db.scalars(user_query)
        user = res.one()

        # store the hashed secret key
        service_account = models.ServiceAccount(
            user=[user],
            name=service_account_create.name,
            description=service_account_create.description,
            hashed_key=hashed_secret_key,
            expiration_duration=service_account_create.expiration_duration,
            expiration=secret_key_information.expiration,
            created_by_id=created_by_id,
        )

        self.db.add(service_account)
        await self.db.commit()
        await self.db.refresh(service_account)

        return self._build_sa_secret(service_account, secret_key_information.key)

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

    async def rotate_key(
        self, id: UUID, modified_by_id: UUID
    ) -> core.schemas.ServiceAccountSecret:
        service_account = await self.get(service_account_id=id, user_id=modified_by_id)

        # generate a secret key for the service account that will be sent to the user
        secret_key_information = self.generate_secret_key(
            expiration_duration=service_account.expiration_duration
        )

        # hash the secret key for storage in database
        hashed_secret_key = password_hasher.hash(secret_key_information.key)

        service_account.hashed_key = hashed_secret_key
        service_account.expiration = secret_key_information.expiration

        service_account.modified_by_id = modified_by_id

        await self.db.commit()
        await self.db.refresh(service_account)

        return self._build_sa_secret(service_account, secret_key_information.key)

    async def expire_key(self, id: UUID, modified_by_id: UUID) -> models.ServiceAccount:
        service_account = await self.get(service_account_id=id, user_id=modified_by_id)

        service_account.expiration = datetime.datetime.now()
        service_account.modified_by_id = modified_by_id

        await self.db.commit()
        await self.db.refresh(service_account)

        return service_account

    def _build_sa_secret(
        self, service_account: models.ServiceAccount, secret_key: str
    ) -> core.schemas.ServiceAccountSecret:
        sa_secret = core.schemas.ServiceAccountSecret.model_validate(service_account)

        # return the generated secret key to the user one time
        # once the response is sent we will no longer know this value
        sa_secret.secret_key = secret_key

        return sa_secret
