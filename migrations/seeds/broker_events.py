import datetime
import uuid

from across_server.core.enums import BrokerEventType
from across_server.db.models import BrokerEvent

sandy_event = BrokerEvent(
    id=uuid.UUID("40890466-71b7-4fa8-9b25-f994cfe53fa8"),
    event_datetime=datetime.datetime.now(),
    type=BrokerEventType.TRANSIENT,
    name="SN2026sandy",
)

broker_events = [sandy_event]
