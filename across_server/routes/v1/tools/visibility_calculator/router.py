from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from across_server.routes.v1.tools.visibility_calculator.service import (
    EphemerisVisibilityService,
)

from .schemas import VisibilityRead, VisibilityResult

router = APIRouter(
    prefix="/visibility-calculator",
    tags=["Tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The visibility calculator does not exist.",
        },
    },
)


@router.get(
    "/calculate/{instrument_id}",
    status_code=status.HTTP_200_OK,
    summary="Visibility Calculator",
    description="Calculate visibility of a satellite from a given location.",
    responses={
        status.HTTP_200_OK: {
            "description": "Return visibility calculation results.",
        },
    },
)
async def visibility_calculator(
    instrument_id: UUID,
    parameters: Annotated[VisibilityRead, Query()],
    visibility_calculator: Annotated[
        EphemerisVisibilityService, Depends(EphemerisVisibilityService)
    ],
) -> VisibilityResult:
    print(parameters.model_dump())
    visibility = await visibility_calculator.get(
        ra=parameters.ra,
        dec=parameters.dec,
        date_range_begin=parameters.date_range_begin,
        date_range_end=parameters.date_range_end,
        hi_res=parameters.hi_res,
        instrument_id=instrument_id,
    )

    return VisibilityResult.model_validate(
        {
            "ra": parameters.ra,
            "dec": parameters.dec,
            "date_range_begin": parameters.date_range_begin,
            "date_range_end": parameters.date_range_end,
            "visibility_windows": visibility.model_dump()["visibility_windows"],
            "instrument_id": instrument_id,
            "hi_res": parameters.hi_res,
        }
    )
