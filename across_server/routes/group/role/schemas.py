from typing import List
import uuid
from pydantic import BaseModel, ConfigDict


class GroupRoleBase(BaseModel):
    name: str


class GroupRoleRead(GroupRoleBase):
    id: uuid.UUID


class GroupRoleCreate(GroupRoleBase):
    pass


class GroupRoleUpdate(GroupRoleBase):
    pass


# This is explicitly defined due to
#   A) parent data should define what data from the child it needs
#   B) pydantic does not handle circular imports, so even if we
#      wanted to import the related schema, we can't use it.
class User(BaseModel):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: str


class GroupRole(GroupRoleRead):
    users: List[User]

    model_config = ConfigDict(from_attributes=True)
