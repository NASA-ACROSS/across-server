from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....db import models
from ....db.database import get_session
from . import schemas
from .exceptions import TelescopeNotFoundException


class TelescopeService:
    """
    Telescope service for managing astronomical Telescope records in the ACROSS SSA system.
    This service handles CRUD operations for Telescope records. This includes retrieval of
    Telescope records in the database.

    Methods
    -------
    get(telescope_id: UUID) -> models.Telescope
        Retrieve the Telescope record with the given id.
    get_many(data: schemas.TelescopeRead) -> Sequence[models.Telescope]
        Retrieves many Telescopes based on the TelescopeRead filter params.
    """

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(
        self,
        telescope_id: UUID,
        include_footprints: bool = True,
        include_filters: bool = True,
    ) -> models.Telescope:
        """
        Retrieve the Telescope record with the given id.
        Parameters
        ----------
        telescope_id : UUID
            the Telescope id
        include_footprints : bool
            Whether to load instrument footprints
        include_filters : bool
            Whether to load instrument filters
        Returns
        -------
        models.Telescope
            The Telescope with the given id
        Raises
        ------
        TelescopeNotFoundException
        """
        query_options = self._get_telescope_query_options(
            include_footprints=include_footprints,
            include_filters=include_filters,
        )

        query = (
            select(models.Telescope)
            .where(models.Telescope.id == telescope_id)
            .options(*query_options)
        )

        result = await self.db.execute(query)
        telescope = result.scalar_one_or_none()

        if telescope is None:
            raise TelescopeNotFoundException(telescope_id)

        return telescope

    def _get_filter(self, data: schemas.TelescopeRead) -> list:
        """
        Build the sql alchemy filter list based on Telescope.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for an telescope
        Parameters
        ----------
        data : schemas.TelescopeRead
            class representing Telescope filter parameters
        Returns
        -------
        list[sqlalchemy.filters]
            list of schedule filter booleans
        """
        data_filter = []

        if data.created_on:
            data_filter.append(
                models.Telescope.created_on > data.created_on
            )  # this should/could be a date-range parameter

        if data.name:
            data_filter.append(
                func.lower(models.Telescope.name).contains(str.lower(data.name))
                | func.lower(models.Telescope.short_name).contains(str.lower(data.name))
            )

        if data.observatory_id:
            data_filter.append(models.Telescope.observatory_id == data.observatory_id)

        if data.observatory_name:
            data_filter.append(
                models.Telescope.observatory.has(
                    func.lower(models.Observatory.name).contains(
                        str.lower(data.observatory_name)
                    )
                    | func.lower(models.Observatory.short_name).contains(
                        str.lower(data.observatory_name)
                    )
                )
            )

        if data.instrument_id:
            data_filter.append(
                models.Telescope.instruments.any(
                    models.Instrument.id == data.instrument_id
                )
            )

        if data.instrument_name:
            data_filter.append(
                models.Telescope.instruments.any(
                    func.lower(models.Instrument.name).contains(
                        str.lower(data.instrument_name)
                    )
                )
                | models.Telescope.instruments.any(
                    func.lower(models.Instrument.short_name).contains(
                        str.lower(data.instrument_name)
                    )
                )
            )

        return data_filter

    def _get_telescope_query_options(
        self,
        include_footprints: bool = False,
        include_filters: bool = False,
    ) -> list:
        options = []
        if include_footprints:
            options.append(
                selectinload(models.Telescope.instruments).selectinload(
                    models.Instrument.footprints
                )
            )
        if include_filters:
            options.append(
                selectinload(models.Telescope.instruments).selectinload(
                    models.Instrument.filters
                )
            )
        return options

    async def get_many(self, data: schemas.TelescopeRead) -> Sequence[models.Telescope]:
        """
        Retrieve a list of Telescope records
        based on the TelescopeRead filter parameters.

        Parameters
        ----------
        data : schemas.TelescopeRead
            class representing Telescope filter parameters

        Returns
        -------
        Sequence[models.Telescope]
            The list of Telescopes
        """
        telescope_filter = self._get_filter(data=data)

        query_options = self._get_telescope_query_options(
            include_footprints=data.include_footprints,
            include_filters=data.include_filters,
        )

        telescope_query = (
            select(models.Telescope).filter(*telescope_filter).options(*query_options)
        )

        result = await self.db.execute(telescope_query)

        telescopes = result.scalars().all()

        return telescopes
