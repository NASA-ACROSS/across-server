import datetime
import uuid
from typing import Optional

from ....core.schemas.base import BaseSchema


class ServiceAccount(BaseSchema):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str]
    expiration: datetime.datetime
    expiration_duration: int
    secret_key: str


class ServiceAccountCreate(BaseSchema):
    name: str
    description: Optional[str]
    expiration_duration: Optional[int]


class ServiceAccountUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    expiration_duration: Optional[int] = None
