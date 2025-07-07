from datetime import datetime
from functools import partial
from typing import Annotated
from uuid import UUID

import anyio.to_thread
import astropy.units as u  # type: ignore[import-untyped]
from across.tools.core.schemas import tle as tle_schemas
from across.tools.ephemeris import (
    Ephemeris,
    compute_ground_ephemeris,
    compute_jpl_ephemeris,
    compute_spice_ephemeris,
    compute_tle_ephemeris,
)
from astropy.coordinates import Latitude, Longitude  # type: ignore[import-untyped]
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .....core.enums.ephemeris_type import EphemerisType
from .....db.database import get_session
from ...observatory import schemas as observatory_schemas
from ...observatory.exceptions import ObservatoryNotFoundException
from ...observatory.service import ObservatoryService
from ...tle.exceptions import TLENotFoundException
from ...tle.service import TLEService
from .exceptions import (
    EphemerisOutsideOperationalRangeException,
    NoEphemerisTypesFoundException,
)


class EphemerisService:
    """
    Service for computing ephemeris data for various observatory and ephemeris
    methods.

    This service provides methods to compute ephemeris data for TLE, JPL,
    SPICE, and ground-based observatories. It retrieves the necessary
    parameters from the database and computes the ephemeris data for a given
    date range. The computations are performed in a separate thread to avoid
    blocking the event loop.

    Methods
    -------
    get_tle_ephem(parameters: TLEParameters, date_range_begin: datetime,
                  date_range_end: datetime, step_size: int = 60) -> Ephemeris
        Computes a TLE ephemeris for the specified date range.

    get_jpl_ephem(parameters: JPLParameters, date_range_begin: datetime,
                  date_range_end: datetime, step_size: int = 60) -> Ephemeris
        Computes a JPL ephemeris for the specified date range.

    get_spice_ephem(parameters: SPICEParameters, date_range_begin: datetime,
                    date_range_end: datetime, step_size: int = 60) -> Ephemeris
        Computes a SPICE ephemeris for the specified date range.

    get_ground_ephem(parameters: GroundParameters, date_range_begin: datetime,
                     date_range_end: datetime, step_size: int = 60) -> Ephemeris
        Computes a ground ephemeris for the specified date range.

    get(observatory_id: UUID, date_range_begin: datetime,
        date_range_end: datetime, step_size: int = 60) -> Ephemeris
        Retrieves the ephemeris data for a given observatory ID and date range.
        It checks the observatory's ephemeris types and computes the appropriate
        ephemeris based on the available parameters. If no valid ephemeris
        type is found, it raises a HTTPException.
    """

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
        Computes a TLE ephemeris for the specified date range.

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
        if tle_model is None:
            raise TLENotFoundException(
                norad_id=parameters.norad_id, epoch=date_range_begin
            )

        tle = tle_schemas.TLE.model_validate(tle_model.__dict__)

        # Perform ephemeris computation in a thread to avoid blocking the event loop
        eph_func = partial(
            compute_tle_ephemeris,
            begin=date_range_begin,
            end=date_range_end,
            step_size=step_size,
            tle=tle,
        )
        ephem = await anyio.to_thread.run_sync(eph_func)

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
        eph_func = partial(
            compute_jpl_ephemeris,
            begin=date_range_begin,
            end=date_range_end,
            step_size=step_size,
            naif_id=parameters.naif_id,
        )
        return await anyio.to_thread.run_sync(eph_func)

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
        eph_func = partial(
            compute_spice_ephemeris,
            begin=date_range_begin,
            end=date_range_end,
            step_size=step_size,
            spice_kernel_url=parameters.spice_kernel_url,
            naif_id=parameters.naif_id,
        )
        return await anyio.to_thread.run_sync(eph_func)

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
        eph_func = partial(
            compute_ground_ephemeris,
            begin=date_range_begin,
            end=date_range_end,
            step_size=step_size,
            longitude=Longitude(parameters.longitude * u.deg),
            latitude=Latitude(parameters.latitude * u.deg),
            height=parameters.height * u.m,
        )
        return await anyio.to_thread.run_sync(eph_func)

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
        if observatory_model is None:
            raise ObservatoryNotFoundException(observatory_id)
        observatory = observatory_schemas.Observatory.model_validate(observatory_model)

        # Check if the requested date range is within the observatory's
        # operational range (if defined)
        if observatory.operational is not None and (
            observatory.operational.begin
            and observatory.operational.end
            and (
                date_range_begin < observatory.operational.begin
                or date_range_end > observatory.operational.end
            )
        ):
            raise EphemerisOutsideOperationalRangeException(
                observatory_id=observatory_id,
                date_range_begin=date_range_begin,
                date_range_end=date_range_end,
            )

        # Compute Ephemeris
        ephemeris_types = observatory.ephemeris_types
        if ephemeris_types is None or len(ephemeris_types) == 0:
            raise NoEphemerisTypesFoundException(observatory_id=observatory_id)

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
        raise NoEphemerisTypesFoundException(observatory_id=observatory_id)
