import uuid
from typing import Tuple

from across.tools import Coordinate
from across.tools.footprint import Footprint as ToolsFootprint

from .....db import models
from ...footprint.schemas import Footprint as FootprintSchema


class ProjectFootprintService:
    async def project_footprint(
        self,
        instrument_ids: list[uuid.UUID],
        observations: list[models.Observation],
        footprints: list[models.Footprint],
    ) -> list[Tuple[ToolsFootprint, uuid.UUID]]:
        instrument_footprint_map: dict[uuid.UUID, ToolsFootprint] = {}
        for instrument_id in instrument_ids:
            instrument_footprints = [
                fp for fp in footprints if fp.instrument_id == instrument_id
            ]
            if instrument_footprints:
                instrument_footprint_map[instrument_id] = (
                    FootprintSchema.orm_to_across_tools_footprint(instrument_footprints)
                )

        projected_footprints = []
        for obs in observations:
            footprint = instrument_footprint_map[obs.instrument_id]
            if obs.pointing_ra is not None and obs.pointing_dec is not None:
                projected_footprint = footprint.project(
                    Coordinate(ra=obs.pointing_ra, dec=obs.pointing_dec),
                    roll_angle=obs.pointing_angle or 0.0,
                )

                projected_footprints.append((projected_footprint, obs.id))

        return projected_footprints
