import datetime
import uuid

from across_server.auth.hashing import password_hasher
from across_server.db.models import ServiceAccount

from .group_roles import treedome_schedule_operations

# use these client credentials to authenticate locally in across-client as this service account
client_id = "961fbb3b-dd5e-45ff-a282-41033e43933d"
client_secret = "prehibernationweek"

# hash the secret key for storage in database
hashed_secret_key = password_hasher.hash(str(client_secret))
# very far away expiration
expiration_date = datetime.datetime.fromisoformat("2126-01-01 00:00:00")

treedome_automation_service_account = ServiceAccount(
    id=uuid.UUID(client_id),
    hashed_key=hashed_secret_key,
    name="Treedome Automation",
    description="Seeded service account for local testing",
    expiration=expiration_date,
    expiration_duration=36525,
    group_roles=[treedome_schedule_operations],
)

service_accounts = [treedome_automation_service_account]
