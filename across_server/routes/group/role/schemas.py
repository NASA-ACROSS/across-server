import uuid

from ....core.schemas.base import BaseSchema


class GroupRoleBase(BaseSchema):
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
class User(BaseSchema):
    id: uuid.UUID
    first_name: str
    last_name: str
    username: str
    email: str


class ServiceAccount(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None
    user: User


class GroupRole(GroupRoleRead):
    users: list[User]
    service_accounts: list[ServiceAccount] | None
