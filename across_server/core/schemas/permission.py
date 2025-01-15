from uuid import UUID

from pydantic import BaseModel


class Permission(BaseModel):
    id: UUID
    name: str
