import uuid

from across_server.db.models import User

from .group_roles import treedome_group_admin, treedome_schedule_operations
from .groups import treedome_space_group
from .roles import across_admin_role

dev = User(
    id=uuid.UUID("173e35fa-9544-49e8-b5b9-d04ea884defb"),
    email="dev@nasa.gov",
    username="across_dev",
    first_name="across",
    last_name="dev",
    created_by_id=None,
    modified_by_id=None,
    roles=[across_admin_role],
)

sandy = User(
    id=uuid.UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
    email="sandy@treedome.space",
    username="SandyTheSquirrel",
    first_name="Sandy",
    last_name="Cheeks",
    created_by_id=None,
    modified_by_id=None,
    group_roles=[treedome_group_admin, treedome_schedule_operations],
    groups=[treedome_space_group],
)

users = [
    dev,
    sandy,
]
