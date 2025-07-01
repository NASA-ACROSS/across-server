from typing import Annotated

from fastapi import APIRouter, Query, status

from across_server.routes.v1.tools.visibility_calculator.schemas import VisibilityRead

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
async def visibility_calculator(
    parameters: Annotated[VisibilityRead, Query()],
) -> dict:
    visibility: dict = {}
    #    visibility = await service.visibility_calculator(**parameters.model_dump())

    return visibility
