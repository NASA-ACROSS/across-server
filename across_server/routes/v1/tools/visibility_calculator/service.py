from datetime import datetime
from functools import partial
from typing import Annotated
from uuid import UUID

import anyio.to_thread
import astropy.units as u  # type: ignore[import-untyped]
from across.tools.visibility import (
    EphemerisVisibility,
    Visibility,
    compute_ephemeris_visibility,
)
from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.core.enums.visibility_type import VisibilityType

from .....db.database import get_session
from ...instrument.schemas import Instrument as InstrumentSchema
from ...instrument.service import InstrumentService
from ...telescope.service import TelescopeService
from ...tools.ephemeris.service import EphemerisService


class VisibilityService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get_ephemeris_visibility(
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
        if constraints is None:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {instrument.name} has no constraints defined.",
            )

        # Compute Ephemeris
        ephemeris = await EphemerisService(self.db).get(
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
            step_size=step_size * u.s,
            observatory_id=observatory_id,
        )
        visibility = await anyio.to_thread.run_sync(vis_function)

        return visibility

    async def get(
        self,
        ra: float,
        dec: float,
        instrument_id: UUID,
        date_range_begin: datetime,
        date_range_end: datetime,
        hi_res: bool,
        min_visibility_duration: int = 0,
    ) -> Visibility:
        # Read in the instrument from UUID
        instrument_model = await InstrumentService(self.db).get(instrument_id)
        if instrument_model is None:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument with ID {instrument_id} not found.",
            )

        # Convert the instrument model to a schema
        instrument = InstrumentSchema.from_orm(instrument_model)
        if instrument.telescope is None:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {instrument.name} has no associated telescope.",
            )

        # Obtain the telescope that hosts this instrument
        telescope = await TelescopeService(self.db).get(instrument.telescope.id)

        if instrument.visibility_type == VisibilityType.EPHEMERIS:
            # Calculate visibility using the instrument schema
            return await self.get_ephemeris_visibility(
                ra=ra,
                dec=dec,
                instrument=instrument,
                observatory_id=telescope.observatory_id,
                date_range_begin=date_range_begin,
                date_range_end=date_range_end,
                hi_res=hi_res,
                min_visibility_duration=min_visibility_duration,
            )
        else:
            raise NotImplementedError(
                f"Visibility type {instrument.visibility_type} is not implemented."
            )
