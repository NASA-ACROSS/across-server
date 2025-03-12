import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from . import schemas
from .service import TelescopeService

router = APIRouter(
    prefix="/telescope",
    tags=["Telescope"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The telescope does not exist.",
        },
    },
)


@router.get(
    "/{telescope_id}",
    summary="Read an telescope",
    description="Read a telescope by a telescope ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Telescope,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Telescope,
            "description": "Return a Telescope",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Telescope not found"},
    },
)
async def get(
    service: Annotated[TelescopeService, Depends(TelescopeService)],
    telescope_id: uuid.UUID,
) -> schemas.Telescope:
    telescope = await service.get(telescope_id)

    return schemas.Telescope.from_orm(telescope)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read telescopes(s)",
    description="Read most recent telescopes based on query params",
    response_model=list[schemas.Telescope],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Telescope],
            "description": "Return a telescope",
        },
    },
)
async def get_many(
    service: Annotated[TelescopeService, Depends(TelescopeService)],
    data: Annotated[schemas.TelescopeRead, Query()],
) -> list[schemas.Telescope]:
    telescopes = await service.get_many(data=data)
    return [schemas.Telescope.from_orm(telescope) for telescope in telescopes]
