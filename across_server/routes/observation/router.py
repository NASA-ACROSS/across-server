import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

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
    response_model=list[schemas.Observation],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Observation],
            "description": "Return a schedule",
        },
    },
)
async def get_many(
    service: Annotated[ObservationService, Depends(ObservationService)],
    data: Annotated[schemas.ObservationRead, Query()],
) -> list[schemas.Observation]:
    observations = await service.get_many(data=data)
    return [schemas.Observation.from_orm(observation) for observation in observations]


@router.get(
    "/{observation_id}",
    summary="Read an observation",
    description="Read an observation by an observation ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Observation,
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
