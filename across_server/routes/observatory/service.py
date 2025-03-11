from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ...db import models
from ...db.database import get_session
from . import schemas
from .exceptions import ObservatoryNotFoundException


class ObservatoryService:
    """
    Observatory service for managing astronomical Observatory records in the ACROSS SSA system.
    This service handles retrieval operations for Observatory records.

    Methods
    -------
    get(observatory_id: UUID) -> models.Observatory
        Retrieve the Observatory record with the given id.
    get_many(data: schemas.ObservatoryRead) -> Sequence[models.Observatory]
        Retrieves many Observatories based on the ObservatoryRead filter params
    """

    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.db = db

    async def get(self, observatory_id: UUID) -> models.Observatory:
        """
        Retrieve the Observatory record with the given id.
        Parameters
        ----------
        observatory_id : UUID
            the Observatory id
        Returns
        -------
        models.Observatory
            The Observatory with the given id
        Raises
        ------
        ObservatoryNotFoundException
        """
        query = select(models.Observatory).where(
            models.Observatory.id == observatory_id
        )

        result = await self.db.execute(query)
        observatory = result.scalar_one_or_none()

        if observatory is None:
            raise ObservatoryNotFoundException(observatory_id)

        return observatory

    def _get_filter(self, data: schemas.ObservatoryRead) -> list:
        """
        Build the sql alchemy filter list based on Observatory.
        Parses whether or not any of the fields are populated, and constructs a list
        of sqlalchemy filter booleans for an observatory

        Parameters
        ----------
        data : schemas.ObservatoryRead
             class representing Observatory filter parameters

        Returns
        -------
        list[sqlalchemy.filters]
            list of schedule filter booleans
        """
        data_filter = []

        if data.created_on:
            data_filter.append(
                models.Observatory.created_on > data.created_on
            )  # this should/could be a date-range parameter

        if data.name:
            data_filter.append(
                func.lower(models.Observatory.name).contains(str.lower(data.name))
                | func.lower(models.Observatory.short_name).contains(
                    str.lower(data.name)
                )
            )

        if data.telescope_id:
            data_filter.append(
                models.Observatory.telescopes.any(
                    models.Telescope.id == data.telescope_id
                )
            )

        if data.telescope_name:
            data_filter.append(
                models.Observatory.telescopes.any(
                    func.lower(models.Telescope.name).contains(
                        str.lower(data.telescope_name)
                    )
                )
                | models.Observatory.telescopes.any(
                    func.lower(models.Telescope.short_name).contains(
                        str.lower(data.telescope_name)
                    )
                )
            )

        if data.type:
            data_filter.append(models.Observatory.observatory_type == data.type)

        return data_filter

    async def get_many(
        self, data: schemas.ObservatoryRead
    ) -> Sequence[models.Observatory]:
        """
        Retrieve a list of Observatory records
        based on the ObservatoryRead filter parameters.

        Parameters
        ----------
        data : schemas.ObservatoryRead
             class representing Observatory filter parameters

        Returns
        -------
        Sequence[models.Observatory]
            The list of Observatory
        """
        observatory_filter = self._get_filter(data=data)

        observatory_query = select(models.Observatory).filter(*observatory_filter)

        result = await self.db.execute(observatory_query)

        observatories = result.scalars().all()

        return observatories
