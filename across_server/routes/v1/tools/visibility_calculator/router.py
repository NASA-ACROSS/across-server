from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from ...instrument.schemas import Instrument as InstrumentSchema
from ...instrument.service import InstrumentService
from ...telescope.exceptions import TelescopeNotFoundException
from ...telescope.service import TelescopeService
from .schemas import VisibilityReadParams, VisibilityResult
from .service import (
    VisibilityCalculatorService,
)

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
    description="Calculate visibility windows of an instrument for a given observation coordinate \n\n Use GET /telescope/ to retrieve a list of telescopes and their associated instruments \n\n WARNING: This is a long running process and is liable to timeout after a strict 60 second execution limit \n\n If you experience issues retrieving results, please scope your date range to be a smaller window or set `hi_res` to `false`",
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
    instrument_service: Annotated[InstrumentService, Depends(InstrumentService)],
    telescope_service: Annotated[TelescopeService, Depends(TelescopeService)],
) -> VisibilityResult:
    instrument_model = await instrument_service.get(instrument_id)

    # Convert the instrument model to a schema
    instrument = InstrumentSchema.from_orm(instrument_model)
    if instrument.telescope is None:
        raise TelescopeNotFoundException(instrument_model.telescope_id)

    # Obtain the telescope that hosts this instrument
    telescope = await telescope_service.get(instrument.telescope.id)

    visibility = await visibility_calculator.calculate_windows(
        ra=parameters.ra,
        dec=parameters.dec,
        instrument=instrument,
        observatory_id=telescope.observatory_id,
        date_range_begin=parameters.date_range_begin,
        date_range_end=parameters.date_range_end,
        hi_res=parameters.hi_res,
        min_visibility_duration=parameters.min_visibility_duration,
    )

    return VisibilityResult.model_validate(
        {
            "visibility_windows": visibility.model_dump()["visibility_windows"],
            "instrument_id": instrument_id,
        }
    )
