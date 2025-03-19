import uuid

from across_server.db.models import GroupRole

from .groups import treedome_space_group
from .permissions import (
    group_read,
    group_role_write,
    group_user_write,
    group_write,
    observatory_write,
    schedule_write,
    telescope_write,
)

treedome_group_admin = GroupRole(
    id=uuid.UUID("f34e9a1b-6843-4dcf-b5a0-12f0d5cb5f45"),
    name="Group Admin",
    permissions=[
        group_user_write,
        group_role_write,
        group_write,
        group_read,
        observatory_write,
        telescope_write,
        schedule_write,
    ],
    group=treedome_space_group,
)

treedome_schedule_operations = GroupRole(
    id=uuid.UUID("12aa89d2-1b77-4a34-9504-063236b58782"),
    name="Schedule Operations",
    permissions=[schedule_write],
    group=treedome_space_group,
)

group_roles = [treedome_group_admin, treedome_schedule_operations]
