from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import FilterNotFoundException


class FilterService:
    """
    Filter service for managing astronomical Filter records in the ACROSS SSA system.
    This service handles CRUD operations for Filter records. This includes retrieval Filter
    records in the database.

    Methods
    -------
    get(filter_id: UUID) -> models.Filter
        Retrieve the Filter record with the given id.
    get_many(data: schemas.InstrumentRead) -> Sequence[models.Filter]
        Retrieves many Filter based on the FilterRead filter params.
    """

    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get(self, filter_id: UUID) -> models.Filter:
        """
        Retrieve the Filter record with the given id.
        Parameters
        ----------
        filter_id : UUID
            the Filter id
        Returns
        -------
        models.Filter
            The Filter with the given id
        Raises
        ------
        FilterNotFoundException
        """
        query = select(models.Filter).where(models.Filter.id == filter_id)

        result = await self.db.execute(query)
        filter = result.scalar_one_or_none()

        if filter is None:
            raise FilterNotFoundException(filter_id)

        return filter

    def _get_filter(self, data: schemas.FilterRead) -> list:
        """
        Build the sql alchemy filter list based on Filter.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for an Filter
        Parameters
        ----------
        data : schemas.FilterRead
             class representing Instrument filter parameters
        Returns
        -------
        list[sqlalchemy.filters]
            list of filter filter booleans
        """
        data_filter = []

        if data.name:
            data_filter.append(
                func.lower(models.Filter.name).contains(str.lower(data.name))
            )

        if data.instrument_id:
            data_filter.append(models.Filter.instrument_id == data.instrument_id)

        if data.instrument_name:
            data_filter.append(
                models.Filter.instrument.has(
                    func.lower(models.Instrument.name).contains(
                        str.lower(data.instrument_name)
                    )
                    | func.lower(models.Instrument.short_name).contains(
                        str.lower(data.instrument_name)
                    )
                )
            )

        if data.covers_wavelength:
            data_filter.extend(
                [
                    models.Filter.min_wavelength <= data.covers_wavelength,
                    models.Filter.max_wavelength >= data.covers_wavelength,
                ]
            )

        return data_filter

    async def get_many(self, data: schemas.FilterRead) -> Sequence[models.Filter]:
        """
        Retrieve a list of Filter records
        based on the FilteRead filter parameters.
        Parameters
        ----------
        data : schemas.FilterRead
             class representing Filter filter parameters
        Returns
        -------
        Sequence[models.Filter]
            The list of Filters
        """
        filter_filter = self._get_filter(data=data)

        filter_query = select(models.Filter).filter(*filter_filter)

        result = await self.db.execute(filter_query)

        filters = result.scalars().all()

        return filters
