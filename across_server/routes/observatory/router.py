import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from . import schemas
from .service import ObservatoryService

router = APIRouter(
    prefix="/observatory",
    tags=["Observatory"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The observatory does not exist.",
        },
    },
)


@router.get(
    "/{observatory_id}",
    summary="Read an observatory",
    description="Read a observatory by a observatory ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Observatory,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Observatory,
            "description": "Return a Observatory",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Observatory not found"},
    },
)
async def get(
    service: Annotated[ObservatoryService, Depends(ObservatoryService)],
    observatory_id: uuid.UUID,
):
    observatory = await service.get(observatory_id)

    return schemas.Observatory.from_orm(observatory)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read observatory(s)",
    description="Read many observatories based on query params",
    response_model=list[schemas.Observatory],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Observatory],
            "description": "Return a observatory",
        },
    },
)
async def get_many(
    service: Annotated[ObservatoryService, Depends(ObservatoryService)],
    data: Annotated[schemas.ObservatoryRead, Query()],
):
    observatories = await service.get_many(data=data)
    return [schemas.Observatory.from_orm(observatory) for observatory in observatories]
