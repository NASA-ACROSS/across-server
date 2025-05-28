import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status

from .... import auth
from . import schemas
from .service import ServiceAccountService

router = APIRouter(
    prefix="/user/{user_id}/service_account",
    tags=["ServiceAccount"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The service account does not exist.",
        },
    },
)


@router.get(
    "/",
    summary="Read service accounts",
    description="Read many service accounts",
    status_code=status.HTTP_200_OK,
)
async def get_many(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
) -> list[schemas.ServiceAccount]:
    service_accounts = await service.get_many(user_id=auth_user.id)
    return [
        schemas.ServiceAccount.model_validate(account) for account in service_accounts
    ]


@router.get(
    "/{service_account_id}",
    summary="Read a service account",
    description="Read a service account by an ID.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "Return a service account",
        },
    },
)
async def get(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    service_account_id: uuid.UUID,
) -> schemas.ServiceAccount:
    service_account = await service.get(service_account_id, user_id=auth_user.id)
    return schemas.ServiceAccount.model_validate(service_account)


@router.post(
    "/",
    summary="Create a service account",
    description="Create a new service account for an ACROSS user.",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.ServiceAccountSecret,
            "description": "The newly created service account",
        },
    },
)
async def create(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    data: schemas.ServiceAccountCreate,
) -> schemas.ServiceAccountSecret:
    service_account, secret_key = await service.create(data, created_by_id=auth_user.id)

    # return the generated secret key to the user one time
    # once the response is sent we will no longer know this value
    service_account_with_secret = schemas.ServiceAccountSecret.model_validate(
        service_account
    )
    service_account_with_secret.secret_key = secret_key
    return service_account_with_secret


@router.patch(
    "/{service_account_id}",
    summary="Update a service account",
    description="Update a service account's information.",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "The updated service account",
        },
    },
)
async def update(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    service_account_id: uuid.UUID,
    data: schemas.ServiceAccountUpdate,
) -> schemas.ServiceAccount:
    service_account = await service.update(
        service_account_id, data, modified_by_id=auth_user.id
    )
    return schemas.ServiceAccount.model_validate(service_account)


@router.delete(
    "/{service_account_id}",
    summary="Delete a service_account",
    description="Expire a service account",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    service_account_id: uuid.UUID,
) -> None:
    await service.expire_key(service_account_id, modified_by_id=auth_user.id)


@router.patch(
    "/{service_account_id}/rotate_key",
    summary="Rotate a service account key",
    description="Rotate service account key and reset expiration based on expiration_duration",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "The rotated service account",
        },
    },
)
async def rotate(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[auth.schemas.AuthUser, Depends(auth.strategies.self_access)],
    service_account_id: uuid.UUID,
) -> schemas.ServiceAccountSecret:
    service_account, secret_key = await service.rotate_key(
        service_account_id, modified_by_id=auth_user.id
    )

    # return the generated secret key to the user one time
    # once the response is sent we will no longer know this value
    service_account_with_secret = schemas.ServiceAccountSecret.model_validate(
        service_account
    )
    service_account_with_secret.secret_key = secret_key
    return service_account_with_secret
