from typing import List
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr

from ...core.schemas import Permission
from ..role.schemas import RoleBase


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: EmailStr


# This is explicitly defined due to
#   A) parent data should define what data from the child it needs
#   B) pydantic does not handle circular imports, so even if we
#      wanted to import the User schema, we can't use it.
class GroupRole(BaseModel):
    id: uuid.UUID
    name: str
    permissions: List[Permission]


class Group(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str
    roles: List[GroupRole]


class User(UserBase):
    id: uuid.UUID
    groups: List[Group]
    roles: List[RoleBase]

    # https://docs.pydantic.dev/latest/concepts/models/#arbitrary-class-instances
    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    username: str
