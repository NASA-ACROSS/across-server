import uuid
from datetime import datetime

from .base import BaseSchema


class ServiceAccountSecret(BaseSchema):
    id: uuid.UUID
    expiration: datetime
    secret_key: str
