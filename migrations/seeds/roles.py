import uuid

from across_server.db import models
from migrations.versions import (
    _2025_05_06_1129_043885e1cd78_permissions_and_roles_data as data,
)

across_admin_role = data.build_role(
    {
        "id": uuid.UUID("e81e0a2b-6883-4def-b540-14f0d5cb5f15"),
        "name": "ACROSS Admin",
        "permissions": ["all_write"],
    },
    models.Role,
    models.Permission,
)

system_role = data.build_role(
    data.role_data["system_role"], models.Role, models.Permission
)

roles = [across_admin_role, system_role]
