import uuid

from across_server.db.models import Permission

# Note: These permissions will likely be data migrations

all_write = Permission(
    id=uuid.UUID("44cffa7a-b531-48c2-a011-51eb11bea6f4"), name="all:write"
)

group_read = Permission(id=uuid.uuid4(), name="group:read")
group_write = Permission(
    id=uuid.UUID("32a6e946-1f29-44d2-a3a7-3c45b5f46499"), name="group:write"
)
group_read = Permission(id=uuid.uuid4(), name="group:read")
user_write = Permission(id=uuid.uuid4(), name="user:write")
service_account_write = Permission(id=uuid.uuid4(), name="user:service_account:write")
service_account_read = Permission(id=uuid.uuid4(), name="user:service_account:read")
group_user_read = Permission(id=uuid.uuid4(), name="group:user:read")
group_user_write = Permission(id=uuid.uuid4(), name="group:user:write")
observatory_write = Permission(id=uuid.uuid4(), name="group:observatory:write")
telescope_write = Permission(id=uuid.uuid4(), name="group:telescope:write")
instrument_write = Permission(id=uuid.uuid4(), name="group:instrument:write")
schedule_write = Permission(id=uuid.uuid4(), name="group:schedule:write")

permissions = [
    all_write,
    group_read,
    group_write,
    group_read,
    user_write,
    service_account_write,
    service_account_read,
    observatory_write,
    telescope_write,
    instrument_write,
    schedule_write,
]
