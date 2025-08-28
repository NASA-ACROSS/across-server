import datetime
import uuid

from .....core.schemas.base import BaseSchema
from ...group.role.schemas import GroupRoleRead


class ServiceAccount(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    expiration: datetime.datetime
    expiration_duration: int
    group_roles: list[GroupRoleRead]


class ServiceAccountCreate(BaseSchema):
    name: str
    description: str | None
    expiration_duration: int | None


class ServiceAccountUpdate(BaseSchema):
    name: str | None = None
    description: str | None = None
    expiration_duration: int | None = None
