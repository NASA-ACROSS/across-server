import uuid

from pydantic import BaseModel

from ....core.schemas.base import BaseSchema


class RoleBase(BaseSchema):
    name: str


# This is explicitly defined due to
#   A) parent data should define what data from the child it needs
#   B) pydantic does not handle circular imports, so even if we
#      wanted to import the User schema, we can't use it.
class Group(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str


class User(BaseSchema):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: str


class Role(RoleBase):
    id: uuid.UUID
    users: list[User]


class RoleCreate(RoleBase):
    permissions: list[str]
