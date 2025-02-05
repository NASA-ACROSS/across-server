import datetime
import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ServiceAccount(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    name: str
    description: Optional[str]
    expiration: datetime.datetime
    expiration_duration: int
    secret_key: str

    # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)


class ServiceAccountCreate(BaseModel):
    name: str
    description: Optional[str]
    expiration_duration: Optional[int]


class ServiceAccountUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    expiration_duration: Optional[int] = None
