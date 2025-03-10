import datetime
from typing import Optional
import uuid

from ....core.schemas.base import BaseSchema


class ServiceAccount(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    expiration: datetime.datetime
    expiration_duration: int
    secret_key: str


class ServiceAccountCreate(BaseSchema):
    name: str
    description: str | None
    expiration_duration: int | None


class ServiceAccountUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    expiration_duration: Optional[int] = None
