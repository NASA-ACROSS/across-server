import datetime
from uuid import UUID

from pydantic import BaseModel, model_serializer

from .enums import PrincipalType


class Group(BaseModel):
    id: UUID
    scopes: list[str]

    @model_serializer
    def serialize(self) -> dict:
        return {"id": str(self.id), "scopes": self.scopes}


class AuthUser(BaseModel):
    id: UUID
    scopes: list[str]
    groups: list[Group]
    type: PrincipalType
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SecretKeySchema(BaseModel):
    key: str
    expiration: datetime.datetime
