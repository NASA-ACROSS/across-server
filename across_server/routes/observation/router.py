from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from ..schedule.access import schedule_access
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


@router.post(
    "/",
    summary="Create an observation",
    description="Create a new observation.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Observation,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Observation,
            "description": "The newly created observation",
        },
    },
    dependencies=[Security(schedule_access, scopes=["group:observation:write"])],
)
async def create(
    service: Annotated[ObservationService, Depends(ObservationService)],
    data: schemas.ObservationCreate,
):
    return await service.create(data)
