from pydantic import BaseModel
from uuid import UUID

class Permission(BaseModel):
    id: UUID
    name: str