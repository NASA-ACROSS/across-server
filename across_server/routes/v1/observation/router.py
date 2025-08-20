import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from across_server.core.schemas.pagination import Page

from . import schemas
from .service import ObservationService

router = APIRouter(
    prefix="/observation",
    tags=["Observation"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The observation does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read observations(s)",
    description="Read the observations based on query params",
    operation_id="get_observations",
    responses={
        status.HTTP_200_OK: {
            "model": Page[schemas.Observation],
            "description": "Return a list of observations",
        },
    },
)
async def get_many(
    service: Annotated[ObservationService, Depends(ObservationService)],
    data: Annotated[schemas.ObservationRead, Query()],
) -> Page[schemas.Observation]:
    observation_tuples = await service.get_many(data=data)

    total_number = observation_tuples[0][1]
    observations = [tuple[0] for tuple in observation_tuples]
    return Page[schemas.Observation].model_validate(
        {
            "total_number": total_number,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                schemas.Observation.from_orm(observation)
                for observation in observations
            ],
        }
    )


@router.get(
    "/{observation_id}",
    summary="Read an observation",
    description="Read an observation by an observation ID.",
    operation_id="get_observation",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Observation,
            "description": "Return an observation",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Observation not found"},
    },
)
async def get(
    service: Annotated[ObservationService, Depends(ObservationService)],
    observation_id: uuid.UUID,
) -> schemas.Observation:
    observation = await service.get(observation_id)

    return schemas.Observation.from_orm(observation)
