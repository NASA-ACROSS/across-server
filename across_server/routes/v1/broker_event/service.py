from collections.abc import Sequence
from typing import Annotated, Tuple
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import BrokerEventNotFoundException


class BrokerEventService:
    """
    BrokerEvent service for managing broker events in the ACROSS SSA system.
    This service handles read operations for BrokerEvent records.

    Methods
    -------
    get(broker_event_id: UUID) -> models.BrokerEvent
        Retrieve the BrokerEvent record with the given id.
    get_many(data: schemas.BrokerEventReadParams) -> Sequence[models.BrokerEvent]
        Retrieves many BrokerEvents based on filter params.
    """

    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get(self, broker_event_id: UUID) -> models.BrokerEvent:
        """
        Retrieve the BrokerEvent record with the given id.

        Parameters
        ----------
        broker_event : UUID
            the BrokerEvent id
        Returns
        -------
        models.BrokerEvent
            The BrokerEvent with the given id
        Raises
        ------
        BrokerEventNotFoundException
        """
        query = select(models.BrokerEvent).where(
            models.BrokerEvent.id == broker_event_id
        )

        result = await self.db.execute(query)
        broker_event = result.scalar_one_or_none()

        if broker_event is None:
            raise BrokerEventNotFoundException(broker_event_id)

        return broker_event

    async def get_many(
        self,
        data: schemas.BrokerEventReadParams,
    ) -> Sequence[Tuple[models.BrokerEvent, int]]:
        """
        Retrieve a list of BrokerEvent records
        based on the query parameters.

        Parameters
        ----------
        data : schemas.BrokerEventReadParams
             class representing BrokerEvent filter parameters
        Returns
        -------
        Sequence[models.BrokerEvent]
            The list of BrokerEvent records
        """
        broker_event_filter = self._get_filter(data=data)

        broker_event_query = (
            select(models.BrokerEvent, func.count().over().label("count"))
            .filter(*broker_event_filter)
            .order_by(models.BrokerEvent.created_on.desc())
            .limit(data.page_limit)
            .offset(data.offset)
        )

        result = await self.db.execute(broker_event_query)

        broker_events = result.tuples().all()

        return broker_events

    def _get_filter(self, data: schemas.BrokerEventReadParams) -> list:
        """
        Build the sql alchemy filter list based on BrokerEvent parameters.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for a BrokerEvent
        Parameters
        ----------
        data : schemas.BrokerEventReadParams
             class representing BrokerEvent filter parameters
        Returns
        -------
        list[sqlalchemy.filters]
            list of broker event filter booleans
        """
        data_filter = []

        if data.name:
            data_filter.append(
                func.lower(models.BrokerEvent.name).contains(str.lower(data.name))
            )

        if data.type:
            data_type_filter = []
            for event_type in data.type:
                data_type_filter.append(models.BrokerEvent.type == event_type)
            data_filter.append(or_(*data_type_filter))

        if data.date_range_begin:
            data_filter.append(
                models.BrokerEvent.event_datetime >= data.date_range_begin
            )

        if data.date_range_end:
            data_filter.append(
                models.BrokerEvent.event_datetime < data.date_range_end,
            )

        return data_filter
