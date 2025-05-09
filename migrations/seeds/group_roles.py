import uuid

from across_server.db.models import GroupRole, Permission

from ..versions import (
    _2025_05_06_1129_043885e1cd78_permissions_and_roles_data as data,
)
from .groups import treedome_space_group

treedome_group_admin = GroupRole(
    id=uuid.UUID("6e53bc64-830a-4daa-a159-bdf2097a8516"),
    name="Group Admin",
    permissions=[
        Permission(**data.permission_data["group_user_write"]),
        Permission(**data.permission_data["group_role_write"]),
        Permission(**data.permission_data["group_write"]),
        Permission(**data.permission_data["group_read"]),
        Permission(**data.permission_data["observatory_write"]),
        Permission(**data.permission_data["telescope_write"]),
        Permission(**data.permission_data["schedule_write"]),
    ],
    group=treedome_space_group,
)

treedome_schedule_operations = GroupRole(
    id=uuid.UUID("cf0675ba-6b40-4539-a2ff-715e3e097db2"),
    name="Schedule Operations",
    permissions=[Permission(**data.permission_data["schedule_write"])],
    group=treedome_space_group,
)

group_roles = [treedome_group_admin, treedome_schedule_operations]
