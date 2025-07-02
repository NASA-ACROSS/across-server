from datetime import datetime
from functools import partial
from typing import Annotated
from uuid import UUID

import anyio.to_thread
import astropy.units as u  # type: ignore[import-untyped]
from across.tools.visibility import EphemerisVisibility, compute_ephemeris_visibility
from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from .....db.database import get_session
from ...instrument.schemas import Instrument as InstrumentSchema
from ...instrument.service import InstrumentService
from ...telescope.service import TelescopeService
from ...tools.ephemeris.service import EphemerisService


class EphemerisVisibilityService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.db = db

    async def get(
        self,
        ra: float,
        dec: float,
        instrument_id: UUID,
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

        # Read in the instrument from UUID
        instrument_model = await InstrumentService(self.db).get(instrument_id)
        instrument_schema = InstrumentSchema.from_orm(instrument_model)

        # Obtain constraint definitions
        constraints = instrument_schema.constraints
        if constraints is None:
            raise HTTPException(
                status_code=404,
                detail=f"Instrument {instrument_schema.name} has no constraints defined.",
            )

        # Obtain the telescope that hosts this instrument
        telescope = await TelescopeService(self.db).get(instrument_model.telescope_id)

        # Compute Ephemeris
        ephemeris = await EphemerisService(self.db).get(
            observatory_id=telescope.observatory_id,
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
            observatory_id=telescope.observatory_id,
        )
        visibility = await anyio.to_thread.run_sync(vis_function)

        return visibility
