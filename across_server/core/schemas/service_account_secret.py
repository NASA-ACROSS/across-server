import uuid
from datetime import datetime

from .base import BaseSchema


class ServiceAccountSecret(BaseSchema):
    id: uuid.UUID
    expiration: datetime
    expiration_duration: int
    secret_key: str
    name: str
    description: str | None
