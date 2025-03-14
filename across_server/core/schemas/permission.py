from uuid import UUID

from .base import BaseSchema


class Permission(BaseSchema):
    id: UUID
    name: str
