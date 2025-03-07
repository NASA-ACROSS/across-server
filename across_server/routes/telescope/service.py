from typing import Annotated, Sequence
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from . import schemas
from .exceptions import TelescopeNotFoundException


class TelescopeService:
    """
    Telescope service for managing astronomical Telescope records in the ACROSS SSA system.
    This service handles CRUD operations for Telescope records. This includes retrieval,
    and creation of new Telescope records in the database.
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

    async def get(self, telescope_id: UUID) -> models.Telescope:
        """
        Retrieve the Telescope record with the given id.
        Parameters
        ----------
        telescope_id : UUID
            the Telescope id
        Returns
        -------
        models.Telescope
            The Telescope with the given id
        Raises
        ------
        TelescopeNotFoundException
        """
        query = select(models.Telescope).where(models.Telescope.id == telescope_id)

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
             class representing Observatory filter parameters
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
            )

        if data.short_name:
            data_filter.append(
                func.lower(models.Telescope.short_name).contains(
                    str.lower(data.short_name)
                )
            )

        return data_filter

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

        telescope_query = select(models.Telescope).filter(*telescope_filter)

        result = await self.db.execute(telescope_query)

        telescopes = result.scalars().all()

        return telescopes
