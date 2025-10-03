from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from across_server.routes.v1.tools.visibility_calculator.service import (
    VisibilityCalculatorService,
)

from .schemas import VisibilityReadParams, VisibilityResult

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
    "/windows/{instrument_id}",
    status_code=status.HTTP_200_OK,
    summary="Calculated Visibility Windows",
    description="Calculate visibility windows of a telescope from a given location.",
    responses={
        status.HTTP_200_OK: {
            "description": "Return visibility window calculation results.",
        },
    },
)
async def calculate_windows(
    instrument_id: UUID,
    parameters: Annotated[VisibilityReadParams, Query()],
    visibility_calculator: Annotated[
        VisibilityCalculatorService, Depends(VisibilityCalculatorService)
    ],
) -> VisibilityResult:
    visibility = await visibility_calculator.calculate_windows(
        ra=parameters.coordinate.ra,
        dec=parameters.coordinate.dec,
        date_range_begin=parameters.date_range_begin,
        date_range_end=parameters.date_range_end,
        hi_res=parameters.hi_res,
        min_visibility_duration=parameters.min_visibility_duration,
        instrument_id=instrument_id,
    )

    return VisibilityResult.model_validate(
        {
            "ra": parameters.coordinate.ra,
            "dec": parameters.coordinate.dec,
            "date_range_begin": parameters.date_range_begin,
            "date_range_end": parameters.date_range_end,
            "visibility_windows": visibility.model_dump()["visibility_windows"],
            "instrument_id": instrument_id,
            "min_visibility_duration": parameters.min_visibility_duration,
            "hi_res": parameters.hi_res,
        }
    )
