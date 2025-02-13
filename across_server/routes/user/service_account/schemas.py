import datetime
import uuid
from typing import List, Optional

from ....core.schemas.base import BaseSchema


class ServiceAccount(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: str | None
    expiration: datetime.datetime
    expiration_duration: int
    secret_key: str
    group_roles: List[str]


class ServiceAccountCreate(BaseSchema):
    name: str
    description: str | None
    expiration_duration: int | None


class ServiceAccountUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None
    expiration_duration: int | None = None
