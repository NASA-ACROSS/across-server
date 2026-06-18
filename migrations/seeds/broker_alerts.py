import datetime
import hashlib
import uuid

from across_server.core.enums import BrokerAlertDataSource, BrokerAlertStatus
from across_server.db.models import BrokerAlert

from .broker_events import sandy_event

sandy_initial_alert = BrokerAlert(
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
    checksum=hashlib.sha512("Sandy's Initial Alert".encode()).hexdigest(),
)

sandy_update_alert = BrokerAlert(
    id=uuid.UUID("19167c32-b558-4eb7-a2bd-60965ad4e723"),
    payload={
        "confirmation_magnitude": "16.0",
        "discovery_filter": "V",
        "discovery_datetime": "2026-04-14T12:34:56",
    },
    status=BrokerAlertStatus.CONFIRMED,
    broker_name="Treedome Broker",
    data_source=BrokerAlertDataSource.BROKER,
    external_event_id=sandy_event.name,
    broker_event_id=sandy_event.id,
    broker_received_on=datetime.datetime.now(),
    checksum=hashlib.sha512("Sandy's Update Alert".encode()).hexdigest(),
)

sandy_classification_alert = BrokerAlert(
    id=uuid.UUID("2ffa8413-9d06-43c7-905b-e61bf20318c0"),
    payload={
        "classification": "SN",
    },
    status=BrokerAlertStatus.CLASSIFIED,
    broker_name="Treedome Broker",
    data_source=BrokerAlertDataSource.BROKER,
    external_event_id=sandy_event.name,
    broker_event_id=sandy_event.id,
    broker_received_on=datetime.datetime.now(),
    checksum=hashlib.sha512("Sandy's Classification Alert".encode()).hexdigest(),
)

broker_alerts = [sandy_initial_alert, sandy_update_alert, sandy_classification_alert]
