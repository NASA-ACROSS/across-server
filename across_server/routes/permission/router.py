from typing import Annotated

from fastapi import APIRouter, Depends, status

from ...core import schemas
from .service import PermissionService

router = APIRouter(
    prefix="/permission",
    tags=["Permission"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The permission does not exist.",
        },
    },
)


@router.get(
    "/",
    summary="Read permissions",
    description="Read many permissions.",
    operation_id="get_permissions",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.Permission],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Permission],
            "description": "A list of permissions",
        },
    },
)
async def get(
    service: Annotated[PermissionService, Depends(PermissionService)],
) -> list[schemas.Permission]:
    permissions = await service.get_all()
    return [schemas.Permission.model_validate(permission) for permission in permissions]
