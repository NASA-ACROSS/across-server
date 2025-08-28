import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from .... import auth, core
from . import schemas
from .service import SystemServiceAccountService

router = APIRouter(
    prefix="/service-account",
    tags=["Internal"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Service account not found.",
        },
    },
)


@router.get(
    "/{service_account_id}",
    summary="Get a system service account",
    description="Rotate service account key and reset expiration based on expiration duration",
    operation_id="get_service_account",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.SystemServiceAccount,
            "description": "The rotated service account",
        },
    },
)
async def get(
    service: Annotated[
        SystemServiceAccountService, Depends(SystemServiceAccountService)
    ],
    principal: Annotated[
        auth.schemas.AuthUser, Security(auth.strategies.system_service_account_access)
    ],
) -> schemas.SystemServiceAccount:
    sa = await service.get(principal.id)

    return schemas.SystemServiceAccount.model_validate(sa)


@router.patch(
    "/{service_account_id}/rotate_key",
    summary="Rotate a service account key",
    description="Rotate service account key and reset expiration based on expiration duration",
    operation_id="service_account_rotate_key",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.SystemServiceAccount,
            "description": "The rotated service account",
        },
    },
)
async def rotate(
    service: Annotated[
        SystemServiceAccountService, Depends(SystemServiceAccountService)
    ],
    principal: Annotated[
        auth.schemas.AuthUser, Security(auth.strategies.system_service_account_access)
    ],
    service_account_id: uuid.UUID,
) -> core.schemas.ServiceAccountSecret:
    return await service.rotate_key(service_account_id, modified_by_id=principal.id)
