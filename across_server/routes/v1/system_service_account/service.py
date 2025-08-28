import datetime
import secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.routes.v1.user.service_account.exceptions import (
    ServiceAccountNotFoundException,
)

from ....auth.hashing import password_hasher
from ....auth.schemas import SecretKeySchema
from ....core import schemas
from ....db import models
from ....db.database import get_session


class SystemServiceAccountService:
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

    async def get(self, id: UUID) -> models.ServiceAccount:
        query = select(models.ServiceAccount).where(models.ServiceAccount.id == id)

        result = await self.db.execute(query)
        service_account = result.scalar_one_or_none()

        if service_account is None:
            raise ServiceAccountNotFoundException(id)

        return service_account

    async def rotate_key(
        self, id: UUID, modified_by_id: UUID
    ) -> schemas.ServiceAccountSecret:
        service_account = await self.get(id=id)

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

    def _build_sa_secret(
        self, service_account: models.ServiceAccount, secret_key: str
    ) -> schemas.ServiceAccountSecret:
        sa_secret = schemas.ServiceAccountSecret.model_validate(service_account)

        # return the generated secret key to the user one time
        # once the response is sent we will no longer know this value
        sa_secret.secret_key = secret_key

        return sa_secret
