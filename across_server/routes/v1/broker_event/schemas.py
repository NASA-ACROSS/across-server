import uuid

from ....core.date_utils import UTCDatetime
from ....core.enums import BrokerEventType
from ....core.schemas.base import BaseSchema
from ....core.schemas.pagination import PaginationParams
from ....db.models import BrokerEvent as BrokerEventModel
from ..broker_alert.schemas import BrokerAlert
from ..localization.schemas import Localization


class BrokerEventBase(BaseSchema):
    """
    A Pydantic model class representing the base BrokerEvent in the ACROSS system.

    Parameters
    ----------
    id : UUID
        Broker event id
    event_datetime : UTCDatetime
        Datetime the event was discovered or detected
    type : BrokerEventType
        Astrophysical type or classification of the event
    name : str
        Name of the event
    """

    id: uuid.UUID
    event_datetime: UTCDatetime
    type: BrokerEventType
    name: str


class BrokerEventReadParams(PaginationParams):
    """
    A Pydantic model class representing the query parameters
    for the BrokerEvent GET methods

    Parameters
    ----------
    type : BrokerEventType, optional
        Astrophysical type or classification of the event
    name : str, optional
        Name of the Instrument
    date_range_begin: UTCDatetime, optional
        Begin datetime to search for event
    date_range_end: UTCDatetime, optional
        End datetime to search for event
    """

    type: list[BrokerEventType] | None = None
    name: str | None = None
    date_range_begin: UTCDatetime | None = None
    date_range_end: UTCDatetime | None = None


class BrokerEvent(BrokerEventBase):
    """
    A Pydantic model class representing a BrokerEvent in the ACROSS system.

    Parameters
    ----------
    localizations : list[Localization]
        Localizations associated with this event
    alerts : list[BrokerAlert]
        Alerts associated with this event

    Methods
    --------
    from_orm:
        Converts ORM BrokerEvent model to a schemas.BrokerEvent object
    """

    localizations: list[Localization]
    broker_alerts: list[BrokerAlert]

    @classmethod
    def from_orm(cls, obj: BrokerEventModel):  #  type: ignore
        """
        Method that converts a models.BrokerEvent record to a schemas.BrokerEvent

        Parameters
        ----------
        obj: BrokerEventModel
        the models.BrokerEvent record

        Returns
        -------
        schemas.BrokerEvent
        """
        return cls(
            id=obj.id,
            event_datetime=obj.event_datetime,
            type=BrokerEventType(obj.type),
            name=obj.name,
            broker_alerts=[
                BrokerAlert.model_validate(alert) for alert in obj.broker_alerts
            ],
            localizations=[
                Localization.from_orm(localization)
                for localization in obj.localizations
            ],
        )
