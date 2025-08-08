import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Security, status

from .... import auth
from ..user.service_account.service import ServiceAccountService
from . import schemas

router = APIRouter(
    prefix="/service-account",
    tags=["Internal"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Service account not found.",
        },
    },
    # Omitted from the openapi spec to avoid confusion from user/service_account routes since this is for internal use only.
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
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    principal: Annotated[
        auth.schemas.AuthUser, Security(auth.strategies.system_service_account_access)
    ],
) -> schemas.SystemServiceAccount:
    sa = await service.get_system(principal.id)

    return schemas.SystemServiceAccount.model_validate(sa)


@router.patch(
    "/{service_account_id}/rotate_key",
    summary="Rotate a service account key",
    description="Rotate service account key and reset expiration based on expiration duration",
    operation_id="service_account_rotate_key",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.SystemServiceAccountSecret,
            "description": "The rotated service account",
        },
    },
)
async def rotate(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    principal: Annotated[
        auth.schemas.AuthUser, Security(auth.strategies.system_service_account_access)
    ],
    service_account_id: uuid.UUID,
) -> schemas.SystemServiceAccountSecret:
    rotated_key = await service.rotate_key(
        service_account_id, modified_by_id=principal.id
    )

    return schemas.SystemServiceAccountSecret.model_validate(rotated_key)
