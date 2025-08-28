import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from . import schemas
from .service import InstrumentService

router = APIRouter(
    prefix="/instrument",
    tags=["Instrument"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The instrument does not exist.",
        },
    },
)


@router.get(
    "/{instrument_id}",
    summary="Read an instrument",
    description="Read an instrument by a instrument ID.",
    operation_id="get_instrument",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Instrument,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Instrument,
            "description": "Return an Instrument",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Instrument not found"},
    },
)
async def get(
    service: Annotated[InstrumentService, Depends(InstrumentService)],
    instrument_id: uuid.UUID,
) -> schemas.Instrument:
    instrument = await service.get(instrument_id)

    return schemas.Instrument.from_orm(instrument)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read instruments(s)",
    description="Read many instruments based on query params",
    operation_id="get_instruments",
    response_model=list[schemas.Instrument],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Instrument],
            "description": "Return an instrument",
        },
    },
)
async def get_many(
    service: Annotated[InstrumentService, Depends(InstrumentService)],
    data: Annotated[schemas.InstrumentRead, Query()],
) -> list[schemas.Instrument]:
    instruments = await service.get_many(data=data)
    return [schemas.Instrument.from_orm(instrument) for instrument in instruments]
