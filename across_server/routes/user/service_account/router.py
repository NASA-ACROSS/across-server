import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Security, status

from .... import auth
from ....db import models
from . import schemas
from .service import ServiceAccountService

router = APIRouter(
    prefix="/user/service_account",
    tags=["ServiceAccount"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The service_account does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.ServiceAccount],
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:read"])
    ],
)
async def get_many(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
):
    return await service.get_many()


@router.get(
    "/{service_account_id}",
    summary="Read a service_account",
    description="Read a service_account by a service_account ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "Return a service_account",
        },
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:read"])
    ],
)
async def get(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    service_account_id: uuid.UUID,
):
    return await service.get(service_account_id)


@router.post(
    "/",
    summary="Create a service_account",
    description="Create a new service_account for an ACROSS user.",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.ServiceAccount,
            "description": "The newly created service_account",
        },
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:write"])
    ],
)
async def create(
    auth_user: Annotated[models.User, Depends(auth.strategies.authenticate)],
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    data: schemas.ServiceAccountCreate,
):
    return await service.create(data, created_by=auth_user)


@router.patch(
    "/{service_account_id}",
    summary="Update a service_account",
    description="Update a service account information for the allowed properties.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "The updated service account",
        },
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:write"])
    ],
)
async def update(
    auth_user: Annotated[models.User, Depends(auth.strategies.authenticate)],
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    service_account_id: uuid.UUID,
    data: schemas.ServiceAccountUpdate,
):
    return await service.update(service_account_id, data, modified_by=auth_user)


@router.delete(
    "/{service_account_id}",
    summary="Delete a service_account",
    description="Expire a service account",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:write"])
    ],
)
async def delete(
    auth_user: Annotated[models.User, Depends(auth.strategies.authenticate)],
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    service_account_id: uuid.UUID,
):
    return await service.expire_key(service_account_id, modified_by=auth_user)
