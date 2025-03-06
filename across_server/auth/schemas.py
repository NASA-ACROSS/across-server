import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, model_serializer


class Group(BaseModel):
    id: UUID
    scopes: List[str]

    @model_serializer
    def serialize(self) -> dict:
        return {"id": str(self.id), "scopes": self.scopes}


class AuthUser(BaseModel):
    id: UUID
    scopes: List[str]
    groups: List[Group]
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SecretKeySchema(BaseModel):
    key: str
    expiration: datetime.datetime
