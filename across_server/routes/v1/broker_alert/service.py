from collections.abc import Sequence
from typing import Annotated, Tuple
from uuid import UUID, uuid4

from fastapi import Depends
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import BrokerAlertNotFoundException, DuplicateBrokerAlertException


class BrokerAlertService:
    """
    BrokerAlert service for managing broker alerts in the ACROSS SSA system.
    This service handles CRUD operations for BrokerAlert records. This includes retrieving
    BrokerAlert records from the database and creating new BrokerAlerts along with their
    associated BrokerEvent and Localization records.

    Methods
    -------
    get(broker_alert_id: UUID) -> models.BrokerAlert
        Retrieve the BrokerAlert record with the given id.
    get_many(data: schemas.BrokerAlertReadParams) -> Sequence[models.BrokerAlert]
        Retrieves many BrokerAlerts based on filter params.
    create(data: schemas.BrokerAlertCreate) -> UUID
        Create a new BrokerAlert record
    """

    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get(self, broker_alert_id: UUID) -> models.BrokerAlert:
        """
        Retrieve the BrokerAlert record with the given id.

        Parameters
        ----------
        broker_alert : UUID
            the BrokerAlert id
        Returns
        -------
        models.BrokerAlert
            The BrokerAlert with the given id
        Raises
        ------
        BrokerAlertNotFoundException
        """
        query = select(models.BrokerAlert).where(
            models.BrokerAlert.id == broker_alert_id
        )

        result = await self.db.execute(query)
        broker_alert = result.scalar_one_or_none()

        if broker_alert is None:
            raise BrokerAlertNotFoundException(broker_alert_id)

        return broker_alert

    async def get_many(
        self,
        data: schemas.BrokerAlertReadParams,
    ) -> Sequence[Tuple[models.BrokerAlert, int]]:
        """
        Retrieve a list of BrokerAlert records
        based on the query parameters.

        Parameters
        ----------
        data : schemas.BrokerAlertReadParams
             class representing BrokerAlert filter parameters
        Returns
        -------
        Sequence[models.BrokerAlert]
            The list of BrokerAlert records
        """
        broker_alert_filter = self._get_filter(data=data)

        broker_alert_query = (
            select(models.BrokerAlert, func.count().over().label("count"))
            .filter(*broker_alert_filter)
            .order_by(models.BrokerAlert.created_on.desc())
            .limit(data.page_limit)
            .offset(data.offset)
        )

        result = await self.db.execute(broker_alert_query)

        broker_alerts = result.tuples().all()

        return broker_alerts

    async def create(
        self,
        data: schemas.BrokerAlertCreate,
    ) -> UUID:
        """
        Create a new BrokerAlert record in the database.
        Checks if the BrokerEvent associated with this Alert
        already exists, and if not, creates it. Also creates the
        Localization record associated with this alert.

        Parameters
        -----------
        data : schemas.BrokerAlertCreate
            The BrokerAlert, BrokerEvent, and Localization data, to be created.
        Returns
        -------
        uuid:
            The UUID of the newly created BrokerAlert

        Raises
        -------
        DuplicateBrokerAlertException
            If a BrokerAlert with the same data already exists in the database.

        Notes
        -----
        The function checks for the existence of an existing BrokerEvent by
        type and name, and checks for the existence of a duplicate BrokerAlert
        by checksum.
        """
        broker_alert = data.to_orm()

        existing = await self._exists([broker_alert.checksum])

        if len(existing):
            raise DuplicateBrokerAlertException(existing[0].id)

        broker_event_query = select(models.BrokerEvent).filter(
            and_(
                models.BrokerEvent.type == data.broker_event_type,
                models.BrokerEvent.name == data.broker_event_name,
            )
        )

        result = await self.db.execute(broker_event_query)

        broker_event = result.scalar_one_or_none()

        if broker_event is None:
            # Create it
            broker_event = models.BrokerEvent(
                id=uuid4(),
                event_datetime=data.broker_event_datetime,
                type=data.broker_event_type,
                name=data.broker_event_name,
            )

        # Create Localization with this BrokerAlert
        localizations = [localization.to_orm() for localization in data.localizations]
        for localization in localizations:
            localization.id = uuid4()
            self.db.add(localization)
            broker_alert.localizations.append(localization)
            broker_event.localizations.append(localization)

        broker_alert.id = uuid4()
        broker_alert.broker_event_id = broker_event.id

        self.db.add(broker_alert)
        self.db.add(broker_event)

        await self.db.commit()
        return broker_alert.id

    async def _exists(self, checksums: list[str]) -> Sequence[models.BrokerAlert]:
        """
        Retrieve the BrokerAlert records with the given checksums.

        Parameters
        ----------
        checksum : list[str]
            the BrokerAlert checksum

        Returns
        -------
        Sequence[models.BrokerAlert]
            returns an array of BrokerAlert records

        """
        query = select(models.BrokerAlert).filter(
            models.BrokerAlert.checksum.in_(checksums)
        )
        result = await self.db.execute(query)
        broker_alerts = result.scalars().all()
        return broker_alerts

    def _get_filter(self, data: schemas.BrokerAlertReadParams) -> list:
        """
        Build the sql alchemy filter list based on BrokerAlert parameters.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for a BrokerAlert
        Parameters
        ----------
        data : schemas.BrokerAlertReadParams
             class representing BrokerAlert filter parameters
        Returns
        -------
        list[sqlalchemy.filters]
            list of broker alert filter booleans
        """
        data_filter = []

        if data.status:
            data_status_filter = []
            for status in data.status:
                data_status_filter.append(models.BrokerAlert.status == status)
            data_filter.append(or_(*data_status_filter))

        if data.broker_name:
            data_filter.append(
                func.lower(models.BrokerAlert.broker_name).contains(
                    str.lower(data.broker_name)
                )
            )

        if data.data_source:
            data_source_filter = []
            for source in data.data_source:
                data_source_filter.append(models.BrokerAlert.data_source == source)
            data_filter.append(or_(*data_source_filter))

        if data.external_event_id:
            data_filter.append(
                func.lower(models.BrokerAlert.external_event_id).contains(
                    str.lower(data.external_event_id)
                )
            )

        if data.broker_event_id:
            data_filter.append(
                models.BrokerAlert.broker_event_id == data.broker_event_id
            )

        if data.broker_received_before:
            data_filter.append(
                models.BrokerAlert.broker_received_on < data.broker_received_before
            )

        if data.broker_received_after:
            data_filter.append(
                models.BrokerAlert.broker_received_on > data.broker_received_after
            )

        return data_filter
