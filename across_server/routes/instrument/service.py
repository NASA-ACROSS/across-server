from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from . import schemas
from .exceptions import InstrumentNotFoundException


class InstrumentService:
    """
    Observatory service for managing astronomical Observatory records in the ACROSS SSA system.
    This service handles CRUD operations for Observatory records. This includes retrieval,
    and creation of new Observatory records in the database.

    Methods
    -------
    get(instrument_id: UUID) -> models.Instrument
        Retrieve the Instrument record with the given id.
    get_many(data: schemas.InstrumentRead) -> Sequence[models.Instrument]
        Retrieves many Instruments based on the Instrument filter params.
    has_footprint()
    """

    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get(self, instrument_id: UUID) -> models.Instrument:
        """
        Retrieve the Instrument record with the given id.
        Parameters
        ----------
        instrument_id : UUID
            the Observatory id
        Returns
        -------
        models.Instrument
            The Instrument with the given id
        Raises
        ------
        InstrumentNotFoundException
        """
        query = select(models.Instrument).where(models.Instrument.id == instrument_id)

        result = await self.db.execute(query)
        instrument = result.scalar_one_or_none()

        if instrument is None:
            raise InstrumentNotFoundException(instrument_id)

        return instrument

    async def has_footprint(self, instrument_id: UUID) -> bool:
        query = select(models.Instrument).where(models.Instrument.id == instrument_id)

        result = await self.db.execute(query)
        instrument = result.scalar_one_or_none()

        if not instrument:
            raise InstrumentNotFoundException(instrument_id)

        return bool(instrument.footprints)

    def _get_filter(self, data: schemas.InstrumentRead) -> list:
        """
        Build the sql alchemy filter list based on Instrument.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for an instrument
        Parameters
        ----------
        data : schemas.InstrumentRead
             class representing Observatory filter parameters
        Returns
        -------
        list[sqlalchemy.filters]
            list of instrument filter booleans
        """
        data_filter = []

        if data.created_on:
            data_filter.append(
                models.Instrument.created_on > data.created_on
            )  # this should/could be a date-range parameter

        if data.name:
            data_filter.append(
                func.lower(models.Instrument.name).contains(str.lower(data.name))
            )

        if data.short_name:
            data_filter.append(
                func.lower(models.Instrument.short_name).contains(
                    str.lower(data.short_name)
                )
            )

        return data_filter

    async def get_many(
        self, data: schemas.InstrumentRead
    ) -> Sequence[models.Instrument]:
        """
        Retrieve a list of Instrument records
        based on the InstrumentRead filter parameters.
        Parameters
        ----------
        data : schemas.InstrumentRead
             class representing Instrument filter parameters
        Returns
        -------
        Sequence[models.Instrument]
            The list of Instruments
        """
        instrument_filter = self._get_filter(data=data)

        instrument_query = select(models.Instrument).filter(*instrument_filter)

        result = await self.db.execute(instrument_query)

        instruments = result.scalars().all()

        return instruments
