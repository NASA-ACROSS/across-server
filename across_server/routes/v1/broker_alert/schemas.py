import uuid

from ....core.date_utils import UTCDatetime
from ....core.enums import BrokerAlertDataSource, BrokerAlertStatus, BrokerEventType
from ....core.schemas.base import BaseSchema
from ....core.schemas.pagination import PaginationParams
from ....db.models import BrokerAlert as BrokerAlertModel
from ..localization.schemas import LocalizationCreate


class BrokerAlertReadParams(PaginationParams):
    """
    A Pydantic model class representing the base BrokerAlert in the ACROSS system.

    Parameters
    ----------
    status : BrokerAlertStatus, optional
        Status of the alert
    broker_name : str, optional
        Name of the broker issuing the alert
    data_source : BrokerAlertDataSource, optional
        Source of the alert
    external_event_id: str, optional
        External name of the BrokerEvent associated with this alert
    broker_event_id: uuid, optional
        ID of the associated BrokerEvent in the ACROSS system
    broker_received_before: UTCDatetime, optional
        Datetime before which the broker received this alert
    broker_received_after: UTCDatetime, optional
        Datetime after which the broker received this alert
    """

    status: list[BrokerAlertStatus] | None = None
    broker_name: str | None = None
    data_source: list[BrokerAlertDataSource] | None = None
    external_event_id: str | None = None
    broker_event_id: uuid.UUID | None = None
    broker_received_before: UTCDatetime | None = None
    broker_received_after: UTCDatetime | None = None


class BrokerAlert(BaseSchema):
    """
    A Pydantic model class representing a BrokerAlert in the ACROSS system.

    Parameters
    ----------
    id : UUID
        Broker alert id
    status : BrokerAlertStatus
        Status of the alert
    broker_name : str
        Name of the broker issuing the alert
    data_source : BrokerAlertDataSource
        Source of the alert
    external_event_id: str
        External name of the BrokerEvent associated with this alert
    broker_event_id: uuid
        ID of the associated BrokerEvent in the ACROSS system
    broker_received_on: datetime
        Datetime the broker received this alert
    payload: dict
        The alert payload, containing unstructured data about the event
    """

    id: uuid.UUID
    status: BrokerAlertStatus
    broker_name: str
    data_source: BrokerAlertDataSource
    external_event_id: str
    broker_event_id: uuid.UUID
    broker_received_on: UTCDatetime
    payload: dict


class BrokerAlertCreate(BaseSchema):
    """
    A Pydantic model class representing a BrokerEvent
    to be created in the ACROSS system.

    Parameters
    ----------
    broker_event_datetime : datetime
        Datetime the associated broker event was discovered or detected
    broker_event_type : BrokerEventType
        Astrophysical type or classification of the broker event
    broker_event_name : str
        Name of the broker event
    localization: Localization
        Localization of the event from this alert

    Methods
    to_orm(self) -> BrokerAlertModel
        Method that creates the ORM record for a broker alert to be serialized into the database.
        This method does not instantiate the associated broker event or localization;
        these records are created within the broker alert service.
    """

    status: BrokerAlertStatus
    broker_name: str
    data_source: BrokerAlertDataSource
    broker_received_on: UTCDatetime
    payload: dict
    broker_event_datetime: UTCDatetime
    broker_event_type: BrokerEventType
    broker_event_name: str
    localizations: list[LocalizationCreate]

    def to_orm(self) -> BrokerAlertModel:
        return BrokerAlertModel(
            payload=self.payload,
            checksum=self.generate_checksum(),
            status=self.status,
            broker_name=self.broker_name,
            data_source=self.data_source,
            external_event_id=self.broker_event_name,
            broker_received_on=self.broker_received_on,
        )
