from datetime import datetime
from functools import partial
from typing import Annotated
from uuid import UUID

import anyio.to_thread
import astropy.units as u  # type: ignore[import-untyped]
from across.tools.visibility import (
    EphemerisVisibility,
    JointVisibility,
    compute_ephemeris_visibility,
    compute_joint_visibility,
)
from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .....core.enums.visibility_type import VisibilityType
from .....db.database import get_session
from ...instrument.schemas import Instrument as InstrumentSchema
from ...tools.ephemeris.service import EphemerisService
from .exceptions import (
    VisibilityConstraintsNotFoundException,
    VisibilityTypeNotImplementedException,
)


class VisibilityCalculatorService:
    def __init__(
        self,
        db: Annotated[AsyncSession, Depends(get_session)],
        ephem_service: Annotated[EphemerisService, Depends(EphemerisService)],
    ) -> None:
        self.db = db
        self.ephem_service = ephem_service

    async def _calc_ephemeris_visibility(
        self,
        ra: float,
        dec: float,
        instrument: InstrumentSchema,
        observatory_id: UUID,
        date_range_begin: datetime,
        date_range_end: datetime,
        hi_res: bool,
        min_visibility_duration: int = 0,
    ) -> EphemerisVisibility:
        # If we're hi-res, then calculate with minute resolution
        if hi_res:
            step_size = 60
        # If we're not hi-res, then calculate with hour resolution
        else:
            step_size = 3600

        # Obtain constraint definitions
        constraints = instrument.constraints
        if not constraints:
            raise VisibilityConstraintsNotFoundException(instrument_id=instrument.id)

        # Compute Ephemeris
        ephemeris = await self.ephem_service.get(
            observatory_id=observatory_id,
            date_range_begin=date_range_begin,
            date_range_end=date_range_end,
            step_size=step_size,
        )

        # Compute visibility
        vis_function = partial(
            compute_ephemeris_visibility,
            begin=Time(date_range_begin),
            end=Time(date_range_end),
            ephemeris=ephemeris,
            constraints=constraints,
            ra=ra,
            dec=dec,
            step_size=step_size * u.s,  # type: ignore
            observatory_id=observatory_id,
            min_vis=min_visibility_duration,
        )
        visibility = await anyio.to_thread.run_sync(vis_function)

        return visibility

    async def calculate_windows(
        self,
        ra: float,
        dec: float,
        instrument: InstrumentSchema,
        observatory_id: UUID,
        date_range_begin: datetime,
        date_range_end: datetime,
        hi_res: bool,
        min_visibility_duration: int = 0,
    ) -> EphemerisVisibility:
        if instrument.visibility_type == VisibilityType.EPHEMERIS:
            # Calculate visibility using the instrument schema
            return await self._calc_ephemeris_visibility(
                ra=ra,
                dec=dec,
                instrument=instrument,
                observatory_id=observatory_id,
                date_range_begin=date_range_begin,
                date_range_end=date_range_end,
                hi_res=hi_res,
                min_visibility_duration=min_visibility_duration,
            )
        else:
            raise VisibilityTypeNotImplementedException(
                f"Visibility type {instrument.visibility_type} is not implemented. Please select an instrument with visibility type {VisibilityType.EPHEMERIS}"
            )

    async def find_joint_visibility(
        self,
        visibilities: list[EphemerisVisibility],
        instrument_ids: list[UUID],
    ) -> JointVisibility:
        # Compute joint visibility
        joint_vis_function = partial(
            compute_joint_visibility,
            visibilities=visibilities,
            instrument_ids=instrument_ids,
        )
        joint_visibility = await anyio.to_thread.run_sync(joint_vis_function)
        return joint_visibility
