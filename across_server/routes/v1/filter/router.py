import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from . import schemas
from .service import FilterService

router = APIRouter(
    prefix="/filter",
    tags=["Filter"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The filter does not exist.",
        },
    },
)


@router.get(
    "/{filter_id}",
    summary="Read a filter",
    description="Read a filter by a filter ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Filter,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Filter,
            "description": "Return a filter",
        },
        status.HTTP_404_NOT_FOUND: {"description": "filter not found"},
    },
)
async def get(
    service: Annotated[FilterService, Depends(FilterService)],
    filter_id: uuid.UUID,
) -> schemas.Filter:
    filter = await service.get(filter_id)

    return schemas.Filter.model_validate(filter)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read filters(s)",
    description="Read many filters based on query params",
    response_model=list[schemas.Filter],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Filter],
            "description": "Return a filter",
        },
    },
)
async def get_many(
    service: Annotated[FilterService, Depends(FilterService)],
    data: Annotated[schemas.FilterRead, Query()],
) -> list[schemas.Filter]:
    filters = await service.get_many(data=data)
    return [schemas.Filter.model_validate(filter) for filter in filters]
