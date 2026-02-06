from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from across_server.routes.v1.tools.project_footprint.service import (
    ProjectFootprintService,
)

from .....db import models
from ...footprint.service import FootprintService
from ...observation.service import ObservationService
from ...schedule.service import ScheduleService
from .schemas import ProjectedFootprint, ProjectFootprintRead

router = APIRouter(
    prefix="/project-footprint",
    tags=["Tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The project footprint tool does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Project Observations Footprint",
    description="Project the footprint of observations based on a list of observation ids or a schedule id",
    responses={
        status.HTTP_200_OK: {
            "description": "Returns a list of projected footprints for the given observations.",
        },
    },
)
async def project_footprint(
    data: Annotated[ProjectFootprintRead, Query()],
    project_footprint_service: Annotated[
        ProjectFootprintService, Depends(ProjectFootprintService)
    ],
    observation_service: Annotated[ObservationService, Depends(ObservationService)],
    schedule_service: Annotated[ScheduleService, Depends(ScheduleService)],
    footprint_service: Annotated[FootprintService, Depends(FootprintService)],
) -> list[ProjectedFootprint]:
    """
    Docstring for project_footprint endpoint
    """
    # Get the observations based on the query parameters
    observations: list[models.Observation] = []
    if data.observation_id:
        observation = await observation_service.get(data.observation_id)
        observations.append(observation)
    elif data.schedule_id:
        schedule = await schedule_service.get(
            data.schedule_id, include_observations=True
        )
        observations.extend(schedule.observations)

    # Get the instrument for each observation and project the footprint
    instrument_ids = set(observation.instrument_id for observation in observations)

    footprints = await footprint_service.get_from_instrument_ids(list(instrument_ids))

    projected_footprints = await project_footprint_service.project_footprint(
        instrument_ids=list(instrument_ids),
        observations=observations,
        footprints=list(footprints),
    )

    return [
        ProjectedFootprint(
            footprint=[
                [(coord.ra, coord.dec) for coord in polygon.coordinates]
                for polygon in projected_footprint.detectors
            ],
            observation_id=observation_id,
        )
        for projected_footprint, observation_id in projected_footprints
    ]
