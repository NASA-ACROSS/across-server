import uuid

from pydantic import BaseModel, ConfigDict

from .role.schemas import GroupRole, GroupRoleRead


class GroupBase(BaseModel):
    name: str
    short_name: str


class GroupRead(GroupBase):
    id: uuid.UUID


# This is explicitly defined due to
#   A) parent data should define what data from the child it needs
#   B) pydantic does not handle circular imports, so even if we
#      wanted to import the User schema, we can't use it.
class User(BaseModel):
    id: uuid.UUID
    username: str
    first_name: str
    last_name: str
    email: str

    group_roles: list[GroupRoleRead]


class Group(GroupRead):
    users: list["User"]
    roles: list[GroupRole]

    model_config = ConfigDict(from_attributes=True)
