import datetime
import uuid

from across_server.routes.v1.group.role.schemas import GroupRoleRead
from across_server.routes.v1.role.schemas import RoleBase

from ....core.schemas.base import BaseSchema


class SystemServiceAccount(BaseSchema):
    id: uuid.UUID
    name: str
    description: str | None = None
    expiration: datetime.datetime
    expiration_duration: int
    roles: list[RoleBase]
    group_roles: list[GroupRoleRead]
