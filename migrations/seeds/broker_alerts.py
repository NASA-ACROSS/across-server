import datetime
import hashlib
import uuid

from across_server.core.enums import BrokerAlertDataSource, BrokerAlertStatus
from across_server.db.models import BrokerAlert

from .broker_events import sandy_event

sandy_alert = BrokerAlert(
    id=uuid.UUID("8984f7f1-3445-4d9d-86ad-de26b289c9ad"),
    payload={
        "discovery_magnitude": "18.0",
        "discovery_filter": "V",
        "discovery_datetime": "2026-04-13T12:34:56",
    },
    status=BrokerAlertStatus.INITIAL,
    broker_name="Treedome Broker",
    data_source=BrokerAlertDataSource.BROKER,
    external_event_id=sandy_event.name,
    broker_event_id=sandy_event.id,
    broker_received_on=datetime.datetime.now(),
    checksum=hashlib.sha512("Sandy's Alert".encode()).hexdigest(),
)

broker_alerts = [sandy_alert]
