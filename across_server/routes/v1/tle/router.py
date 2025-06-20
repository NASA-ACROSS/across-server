from typing import Annotated

from fastapi import APIRouter, Depends, status

from .... import auth
from . import schemas
from .service import TLEService

router = APIRouter(
    prefix="/tle",
    tags=["TLE"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The TLE does not exist.",
        },
    },
)


@router.post(
    "/",
    summary="Create a TLE",
    description="Create a new TLE for ACROSS.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {},
    },
    response_model=schemas.TLE,
    dependencies=[Depends(auth.strategies.global_access)],
)
async def create(
    TLE_service: Annotated[TLEService, Depends(TLEService)],
    data: schemas.TLECreate,
) -> schemas.TLE:
    tle = await TLE_service.create(data)
    return schemas.TLE.model_validate(tle)
