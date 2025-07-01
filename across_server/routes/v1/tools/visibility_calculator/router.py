from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, status

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
    "/calculate",
    status_code=status.HTTP_200_OK,
    summary="Visibility Calculator",
    description="Calculate visibility of a satellite from a given location.",
    responses={
        status.HTTP_200_OK: {
            "description": "Return visibility calculation results.",
        },
    },
)
def visibility_calculator(
    begin: datetime, end: datetime, ra: float, dec: float, instrument: UUID
) -> dict:
    return {}
