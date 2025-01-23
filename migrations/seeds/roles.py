import uuid

from across_server.db.models import Role

from .permissions import all_write, service_account_read, service_account_write

across_admin_role = Role(
    id=uuid.UUID("e81e0a2b-6883-4def-b540-14f0d5cb5f15"),
    name="ACROSS Admin",
    permissions=[all_write],
)

user_service_account_role = Role(
    id=uuid.UUID("fda33adf-1d5b-4b01-878e-90d0c0888e2a"),
    name="ACROSS Service Account",
    permissions=[service_account_read, service_account_write],
)

roles = [across_admin_role]
