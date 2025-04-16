from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...core.enums.ephemeris_type import EphemerisType
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

    async def _get_ephem_parameters(
        self, observatories: Sequence[models.Observatory]
    ) -> Sequence[models.Observatory]:
        """
        Fetch and populate the ephemeris parameters for the given observatories.

        Parameters
        ----------
        observatories : list[models.Observatory]
            The observatories for which to fetch ephemeris parameters.

        Returns
        -------
        list[models.Observatory]
            The observatories with their ephemeris parameters populated.

        Raises
        ------
        ValueError
            If the ephemeris type is unknown.
        """
        ephemeris_types = {
            et.ephemeris_type for obs in observatories for et in obs.ephemeris_types
        }

        observatory_ids = [x.id for x in observatories]

        ephemeris_dictionaries: dict = {}
        for etype in ephemeris_types:
            parameter_model: type[
                models.JPLEphemerisParameters
                | models.TLEParameters
                | models.SpiceKernelParameters
                | models.EarthLocationParameters
            ]

            # Determine the model based on the ephemeris type
            match etype:
                case EphemerisType.JPL.value:
                    parameter_model = models.JPLEphemerisParameters
                case EphemerisType.TLE.value:
                    parameter_model = models.TLEParameters
                case EphemerisType.SPICE.value:
                    parameter_model = models.SpiceKernelParameters
                case EphemerisType.GROUND.value:
                    parameter_model = models.EarthLocationParameters
                case _:
                    raise ValueError(f"Unknown ephemeris type: {etype}")

            ephemeris_dictionaries[etype] = {}
            # Fetch the parameters for the observatory and populate them
            param_query = select(parameter_model).where(
                parameter_model.observatory_id.in_(observatory_ids)
            )
            param_result = await self.db.execute(param_query)
            ephem_parameters = param_result.scalars()
            for ep in ephem_parameters:
                ephemeris_dictionaries[etype][ep.observatory_id] = ep  # type: ignore

        for observatory in observatories:
            for obs_etype in observatory.ephemeris_types:
                obs_etype.parameters = ephemeris_dictionaries[obs_etype.ephemeris_type][
                    observatory.id
                ]

        return observatories

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
        query = (
            select(models.Observatory)
            .where(models.Observatory.id == observatory_id)
            .options(
                selectinload(models.Observatory.ephemeris_types),
            )
        )

        result = await self.db.execute(query)
        observatory = result.scalar_one_or_none()

        if observatory is None:
            raise ObservatoryNotFoundException(observatory_id)

        # Fetch the correct ephemeris parameters
        observatories = await self._get_ephem_parameters([observatory])
        return observatories[0]

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

        # Filter by telescope name
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

        # Filter by ephemeris type
        if data.ephemeris_type:
            data_filter.append(
                models.Observatory.ephemeris_types.any(
                    models.ObservatoryEphemerisType.ephemeris_type.in_(
                        data.ephemeris_type
                    )
                )
            )

        if data.type:
            data_filter.append(models.Observatory.type == data.type)

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
        observatory_query = (
            select(models.Observatory)
            .filter(*observatory_filter)
            .options(
                selectinload(models.Observatory.ephemeris_types),
            )
        )

        result = await self.db.execute(observatory_query)

        observatories = result.scalars().all()

        # Fetch the correct ephemeris parameters
        # for each observatory
        return await self._get_ephem_parameters(observatories)
