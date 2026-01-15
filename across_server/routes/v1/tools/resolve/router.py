from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from .schemas import NameResolver, NameResolverRead
from .service import NameResolveService

router = APIRouter(
    prefix="/resolve",
    tags=["Tools"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The name resolver does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Resolve a target name",
    description="Resolve a target name into coordinates",
    responses={
        status.HTTP_200_OK: {
            "description": "Return resolved target coordinates.",
        },
    },
)
async def resolve(
    data: Annotated[NameResolverRead, Query()],
    resolve_service: Annotated[NameResolveService, Depends(NameResolveService)],
) -> NameResolver:
    return await resolve_service.resolve(data)
