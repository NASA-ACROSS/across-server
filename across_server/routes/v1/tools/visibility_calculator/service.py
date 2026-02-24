from datetime import datetime
from functools import partial
from typing import Annotated
from uuid import UUID

import anyio.to_thread
import astropy.units as u  # type: ignore[import-untyped]
from across.tools.core.schemas import Coordinate, Polygon
from across.tools.footprint import Footprint as ToolsFootprint
from across.tools.footprint.schemas import Pointing
from across.tools.visibility import (
    EphemerisVisibility,
    JointVisibility,
    compute_ephemeris_visibility,
    compute_joint_visibility,
)
from across.tools.visibility.constraints import PointingConstraint
from astropy.time import Time  # type: ignore[import-untyped]
from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from .....core.enums.observation_strategy import ObservationStrategy
from .....core.enums.visibility_type import VisibilityType
from .....db import models
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
            constraints = []

        # Compute Ephemeris
        ephemeris = await self.ephem_service.get(
            observatory_id=observatory_id,
            date_range_begin=date_range_begin,
            date_range_end=date_range_end,
            step_size=step_size,
        )

        # Check if instrument observation strategy is survey, and if so
        # pull footprint, observations, and transform to pointing constraints
        if instrument.observation_strategy == ObservationStrategy.SURVEY:
            pointing_constraint = await self._get_pointing_constraint(
                instrument, date_range_begin, date_range_end
            )
            if pointing_constraint is not None:
                constraints.append(pointing_constraint)

        if not len(constraints):
            raise VisibilityConstraintsNotFoundException(instrument_id=instrument.id)

        # Compute visibility
        vis_function = partial(
            compute_ephemeris_visibility,
            begin=Time(date_range_begin),
            end=Time(date_range_end),
            ephemeris=ephemeris,
            constraints=constraints,  # type: ignore[arg-type]
            ra=ra,
            dec=dec,
            step_size=step_size * u.s,  # type: ignore
            observatory_id=observatory_id,
            min_vis=min_visibility_duration,
        )
        visibility = await anyio.to_thread.run_sync(vis_function)

        return visibility

    async def _get_pointing_constraint(
        self,
        instrument: InstrumentSchema,
        date_range_begin: datetime,
        date_range_end: datetime,
    ) -> PointingConstraint | None:
        """
        Query the observations for a survey instrument,
        convert them to ACROSS-tools Pointings, and build the
        corresponding PointingConstraint.

        Parameters
        ----------
        instrument: schemas.Instrument
            The Instrument belonging to the observations
        date_range_begin: datetime
            The begin time to search for observations
        date_range_end: datetime
            The end time to search for observations

        Returns
        -------
        PointingConstraint
            A constraint built from the instrument pointings
        """
        # Build a subquery to retrieve latest matching schedule ID
        schedule2 = aliased(models.Schedule)
        schedule_subquery = (
            select(schedule2.id)
            .where(
                and_(
                    schedule2.telescope_id == models.Instrument.telescope_id,
                    schedule2.date_range_end >= date_range_begin,
                    schedule2.date_range_begin <= date_range_end,
                    schedule2.id == models.Observation.schedule_id,
                )
            )
            .order_by(schedule2.created_on.desc())
            .limit(1)
            .scalar_subquery()
        )

        # Query observations from most recent schedule that match inputs
        query = (
            select(models.Observation)
            .join(
                models.Instrument,
                models.Instrument.id == models.Observation.instrument_id,
            )
            .join(models.Schedule, models.Schedule.id == schedule_subquery)
            .where(
                and_(
                    models.Observation.instrument_id == instrument.id,
                    models.Observation.date_range_begin >= date_range_begin,
                    models.Observation.date_range_end <= date_range_end,
                )
            )
        )

        result = await self.db.execute(query)
        observations = result.scalars().all()

        # Get instrument footprints
        instrument_footprints = instrument.footprints
        if not instrument_footprints:
            return None

        # Transform to tools Footprint
        detectors = []
        for footprint in instrument_footprints:
            coordinates = [Coordinate(ra=coord.x, dec=coord.y) for coord in footprint]
            detectors.append(Polygon(coordinates=coordinates))

        tools_footprint = ToolsFootprint(detectors=detectors)

        # Project and rotate footprints
        pointings: list[Pointing] = []
        for obs in observations:
            if obs.pointing_ra is not None and obs.pointing_dec is not None:
                projected_footprint = tools_footprint.project(
                    Coordinate(ra=obs.pointing_ra, dec=obs.pointing_dec),
                    roll_angle=obs.pointing_angle or 0.0,
                )

                # Transform to pointing object
                pointings.append(
                    Pointing(
                        footprint=projected_footprint,
                        start_time=obs.date_range_begin,
                        end_time=obs.date_range_end,
                    )
                )

        pointing_constraint = PointingConstraint(pointings=pointings)

        return pointing_constraint

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
