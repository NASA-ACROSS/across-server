from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

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
    operation_id="create_tle",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {},
    },
    response_model=schemas.TLE,
    dependencies=[Security(auth.strategies.global_access, scopes=["system:tle:write"])],
)
async def create(
    TLE_service: Annotated[TLEService, Depends(TLEService)],
    data: schemas.TLECreate,
) -> schemas.TLE:
    tle = await TLE_service.create(data)
    return schemas.TLE.model_validate(tle)
