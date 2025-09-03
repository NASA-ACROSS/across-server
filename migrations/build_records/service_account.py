import uuid
from typing import Type, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import DeclarativeBase

from across_server.auth.hashing import password_hasher
from across_server.auth.schemas import SecretKeySchema
from across_server.core import config
from across_server.routes.v1.user.service_account.service import ServiceAccountService


class ServiceAccountData(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    expiration_duration: int | None = None  # days


T = TypeVar("T", bound=DeclarativeBase)


def build(
    service_account_data: ServiceAccountData,
    service_account_model: Type[T],
) -> tuple[T, SecretKeySchema]:
    # Use the default duration; the service will have a process to rotate the key accordingly.
    expiration_duration = (
        service_account_data.expiration_duration
        or config.SERVICE_ACCOUNT_EXPIRATION_DURATION
    )

    service_account_data.expiration_duration = expiration_duration

    secret = ServiceAccountService.generate_secret_key(expiration_duration)

    if config.is_local():
        # override the generated key with the default "local" key
        secret.key = "local-service-account-key"

    # hash the secret key for storage in database
    hashed_secret_key = password_hasher.hash(secret.key)

    record = service_account_model(
        **service_account_data.model_dump(),
        hashed_key=hashed_secret_key,
        expiration=secret.expiration,
    )

    return record, secret
