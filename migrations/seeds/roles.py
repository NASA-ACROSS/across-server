import uuid
from across_server.db.models import Role
from .permissions import all_write

across_admin_role = Role(
    id=uuid.UUID("e81e0a2b-6883-4def-b540-14f0d5cb5f15"),
    name="ACROSS Admin",
    permissions=[all_write],
)

roles = [across_admin_role]
