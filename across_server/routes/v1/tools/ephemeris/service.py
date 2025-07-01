from datetime import datetime
from typing import Annotated
from uuid import UUID

import anyio
import anyio.to_thread
from across.tools.core.schemas import tle as tle_schemas
from across.tools.ephemeris import (
    Ephemeris,
    compute_ground_ephemeris,
    compute_jpl_ephemeris,
    compute_spice_ephemeris,
    compute_tle_ephemeris,
)
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.db.database import get_session
from across_server.routes.v1.observatory import schemas as observatory_schemas
from across_server.routes.v1.observatory.service import ObservatoryService
from across_server.routes.v1.tle.service import TLEService


class EphemerisService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db: AsyncSession = db

    async def get_tle_ephem(
        self,
        parameters: observatory_schemas.TLEParameters,
        date_range_begin: datetime,
        date_range_end: datetime,
        step_size: int = 60,
    ) -> Ephemeris:
        """
        Retrieve the TLE Ephemeris for a given observatory TLE ephemeris
        parameters.

        Parameters
        ----------
        parameters : observatory_schemas.TLEParameters
            The TLE parameters containing the NORAD ID and other relevant
            information.
        date_range_begin : datetime
            The start date of the date range for which to compute the
            ephemeris.
        date_range_end : datetime
            The end date of the date range for which to compute the ephemeris.
        step_size : int, optional
            The step size in seconds for the ephemeris computation, by default
            60 seconds.

        Raises
        ------
        HTTPException
            If no TLE is found for the given NORAD ID or if the date range is
            invalid.


        Returns
        -------
        TLEEphemeris
            The computed TLE ephemeris for the specified date range.
        """

        tle_model = await TLEService(self.db).get(
            norad_id=parameters.norad_id, epoch=date_range_begin
        )
        tle = tle_schemas.TLE.model_validate(tle_model)

        if not tle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No TLE found for norad_id {parameters.norad_id}",
            )

        # Perform ephemeris computation in a thread to avoid blocking the event loop
        ephem = await anyio.to_thread.run_sync(
            compute_tle_ephemeris,
            date_range_begin,
            date_range_end,
            step_size,
            tle,
        )

        return ephem

    async def get_jpl_ephem(
        self,
        parameters: observatory_schemas.JPLParameters,
        date_range_begin: datetime,
        date_range_end: datetime,
        step_size: int = 60,
    ) -> Ephemeris:
        """
        Retrieve the JPL Ephemeris for a given observatory JPL ephemeris
        parameters.

        Parameters
        ----------
        parameters : observatory_schemas.JPLParameters
            The JPL parameters containing the target and observer information.
        date_range_begin : datetime
            The start date of the date range for which to compute the ephemeris.
        date_range_end : datetime
            The end date of the date range for which to compute the ephemeris.

        Returns
        -------
        JPLEphemeris
            The computed JPL ephemeris for the specified date range.
        """
        return await anyio.to_thread.run_sync(
            compute_jpl_ephemeris,
            date_range_begin,
            date_range_end,
            step_size,
            parameters.naif_id,
        )

    async def get_spice_ephem(
        self,
        parameters: observatory_schemas.SPICEParameters,
        date_range_begin: datetime,
        date_range_end: datetime,
        step_size: int = 60,
    ) -> Ephemeris:
        """
        Retrieve the SPICE Ephemeris for a given observatory SPICE ephemeris
        parameters.

        Parameters
        ----------
        parameters : observatory_schemas.SPICEParameters
            The SPICE parameters containing the target and observer information.
        date_range_begin : datetime
            The start date of the date range for which to compute the ephemeris.
        date_range_end : datetime
            The end date of the date range for which to compute the ephemeris.

        Returns
        -------
        SPICEEphemeris
            The computed SPICE ephemeris for the specified date range.
        """
        return await anyio.to_thread.run_sync(
            compute_spice_ephemeris,
            date_range_begin,
            date_range_end,
            step_size,
            parameters.spice_kernel_url,
            parameters.naif_id,
        )

    async def get_ground_ephem(
        self,
        parameters: observatory_schemas.GroundParameters,
        date_range_begin: datetime,
        date_range_end: datetime,
        step_size: int = 60,
    ) -> Ephemeris:
        """
        Retrieve the Ground Ephemeris for a given observatory ground ephemeris
        parameters.

        Parameters
        ----------
        parameters : observatory_schemas.GroundParameters
            The ground parameters containing the location information.
        date_range_begin : datetime
            The start date of the date range for which to compute the ephemeris.
        date_range_end : datetime
            The end date of the date range for which to compute the ephemeris.

        Returns
        -------
        GroundEphemeris
            The computed ground ephemeris for the specified date range.
        """
        return await anyio.to_thread.run_sync(
            compute_ground_ephemeris,
            date_range_begin,
            date_range_end,
            step_size,
            parameters.longitude,
            parameters.latitude,
            parameters.height,
        )

    async def get(
        self,
        observatory_id: UUID,
        date_range_begin: datetime,
        date_range_end: datetime,
        step_size: int = 60,
    ) -> Ephemeris:
        """
        Retrieve the Ephemeris Types for a given observatory.

        Parameters
        ----------
        observatory_id : UUID
            The ID of the observatory to retrieve ephemeris types for.

        Returns
        -------
        list[schemas.EphemerisType]
            A list of Ephemeris Types associated with the observatory.
        """

        # Obtain the observatory that hosts this telescope
        observatory_model = await ObservatoryService(self.db).get(observatory_id)
        observatory = observatory_schemas.Observatory.model_validate(observatory_model)

        # Compute Ephemeris
        ephemeris_types = observatory.ephemeris_types
        if ephemeris_types is None or len(ephemeris_types) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No ephemeris types found for observatory {observatory_id}",
            )
        # Sort ephemeris types by priority
        ephemeris_types.sort(key=lambda x: x.priority)

        # Iterate through the ephemeris types and return the first valid one
        for etype in ephemeris_types:
            if etype.ephemeris_type == EphemerisType.TLE and isinstance(
                etype.parameters, observatory_schemas.TLEParameters
            ):
                return await self.get_tle_ephem(
                    parameters=etype.parameters,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    step_size=step_size,
                )
            if etype.ephemeris_type == EphemerisType.GROUND and isinstance(
                etype.parameters, observatory_schemas.GroundParameters
            ):
                return await self.get_ground_ephem(
                    parameters=etype.parameters,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    step_size=step_size,
                )
            if etype.ephemeris_type == EphemerisType.SPICE and isinstance(
                etype.parameters, observatory_schemas.SPICEParameters
            ):
                return await self.get_spice_ephem(
                    parameters=etype.parameters,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    step_size=step_size,
                )
            if etype.ephemeris_type == EphemerisType.JPL and isinstance(
                etype.parameters, observatory_schemas.JPLParameters
            ):
                return await self.get_jpl_ephem(
                    parameters=etype.parameters,
                    date_range_begin=date_range_begin,
                    date_range_end=date_range_end,
                    step_size=step_size,
                )
        raise ValueError(
            f"No valid ephemeris type found for observatory {observatory_id}"
        )
