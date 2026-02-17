import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from ...footprint.exceptions import FootprintNotFoundException
from ...footprint.service import FootprintService
from ...observation.exceptions import ObservationNotFoundException
from ...observation.service import ObservationService
from ...schedule.exceptions import ScheduleNotFoundException
from ...schedule.service import ScheduleService
from .schemas import ProjectedObservation
from .service import (
    ProjectFootprintService,
)

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
    "/observation/{observation_id}",
    status_code=status.HTTP_200_OK,
    summary="Project Observation Footprint",
    description="Project the footprint of an observation based on an observation id",
    responses={
        status.HTTP_200_OK: {
            "description": "Returns the projected footprint for the given observation.",
        },
    },
)
async def project_observation_footprint(
    observation_id: uuid.UUID,
    project_footprint_service: Annotated[
        ProjectFootprintService, Depends(ProjectFootprintService)
    ],
    observation_service: Annotated[ObservationService, Depends(ObservationService)],
    footprint_service: Annotated[FootprintService, Depends(FootprintService)],
) -> ProjectedObservation:
    # Get the observations based on the query parameters
    observation = await observation_service.get(observation_id)

    if observation is None:
        raise ObservationNotFoundException(observation_id)

    # Get the instrument for each observation and project the footprint
    instrument_id = observation.instrument_id

    footprints = await footprint_service.get_from_instrument_ids([instrument_id])

    if footprints is None:
        raise FootprintNotFoundException(instrument_id)

    projected_footprints = await project_footprint_service.project_footprint(
        instrument_ids=[instrument_id],
        observations=[observation],
        footprints=list(footprints),
    )

    return projected_footprints[0]


@router.get(
    "/schedule/{schedule_id}",
    status_code=status.HTTP_200_OK,
    summary="Project Schedule Footprints",
    description="Project the footprint of observations based on a schedule id",
    responses={
        status.HTTP_200_OK: {
            "description": "Returns a list of projected footprints for the given schedule.",
        },
    },
)
async def project_schedule_footprints(
    schedule_id: uuid.UUID,
    project_footprint_service: Annotated[
        ProjectFootprintService, Depends(ProjectFootprintService)
    ],
    schedule_service: Annotated[ScheduleService, Depends(ScheduleService)],
    footprint_service: Annotated[FootprintService, Depends(FootprintService)],
) -> list[ProjectedObservation]:
    # Get the observations based on the query parameters
    schedule = await schedule_service.get(schedule_id, include_observations=True)

    if schedule is None:
        raise ScheduleNotFoundException(schedule_id)

    observations = schedule.observations

    # Get the instrument for each observation and project the footprint
    instrument_ids = set(observation.instrument_id for observation in observations)

    footprints = await footprint_service.get_from_instrument_ids(list(instrument_ids))

    projected_footprints = await project_footprint_service.project_footprint(
        instrument_ids=list(instrument_ids),
        observations=observations,
        footprints=list(footprints),
    )

    return projected_footprints
