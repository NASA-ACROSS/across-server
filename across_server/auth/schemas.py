from typing import List
from uuid import UUID

from pydantic import BaseModel


class Group(BaseModel):
    id: str
    scopes: List[str]


class AuthUser(BaseModel):
    id: UUID
    scopes: List[str]
    groups: List[Group]


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
