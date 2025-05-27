import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, model_serializer


class Group(BaseModel):
    id: UUID
    scopes: list[str]

    @model_serializer
    def serialize(self) -> dict:
        return {"id": str(self.id), "scopes": self.scopes}


class AuthUserType(Enum):
    USER = "user"
    SERVICE_ACCOUNT = "service_account"


class GrantType(Enum):
    CLIENT_CREDENTIALS = "client_credentials"
    JWT = "urn:ietf:params:oauth:grant-type:jwt-bearer"


class AuthUser(BaseModel):
    id: UUID
    scopes: list[str]
    groups: list[Group]
    type: str
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SecretKeySchema(BaseModel):
    key: str
    salt: str
    expiration: datetime.datetime
