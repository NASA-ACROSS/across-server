import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, Security, status

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
    response_model=List[schemas.ServiceAccount],
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:read"]),
        Depends(auth.strategies.self_access),
    ],
)
async def get_many(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[
        auth.strategies.AuthUser, Depends(auth.strategies.self_access)
    ],
):
    return await service.get_many(auth_user)


@router.get(
    "/{service_account_id}",
    summary="Read a service account",
    description="Read a service account by an ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "Return a service account",
        },
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:read"]),
        Depends(auth.strategies.self_access),
    ],
)
async def get(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[
        auth.strategies.AuthUser, Depends(auth.strategies.self_access)
    ],
    service_account_id: uuid.UUID,
):
    return await service.get(service_account_id, user_id=auth_user.id)


@router.post(
    "/",
    summary="Create a service account",
    description="Create a new service account for an ACROSS user.",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.ServiceAccount,
            "description": "The newly created service account",
        },
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:write"])
    ],
)
async def create(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[
        auth.strategies.AuthUser, Depends(auth.strategies.self_access)
    ],
    data: schemas.ServiceAccountCreate,
):
    return await service.create(data, created_by_id=auth_user.id)


@router.patch(
    "/{service_account_id}",
    summary="Update a service account",
    description="Update a service account's information.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ServiceAccount,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ServiceAccount,
            "description": "The updated service account",
        },
    },
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:write"]),
        Depends(auth.strategies.self_access),
    ],
)
async def update(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[
        auth.strategies.AuthUser, Depends(auth.strategies.self_access)
    ],
    service_account_id: uuid.UUID,
    data: schemas.ServiceAccountUpdate,
):
    return await service.update(service_account_id, data, modified_by_id=auth_user.id)


@router.delete(
    "/{service_account_id}",
    summary="Delete a service_account",
    description="Expire a service account",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[
        Security(auth.strategies.global_access, scopes=["user:service_account:write"]),
        Depends(auth.strategies.self_access),
    ],
)
async def delete(
    service: Annotated[ServiceAccountService, Depends(ServiceAccountService)],
    auth_user: Annotated[
        auth.strategies.AuthUser, Depends(auth.strategies.self_access)
    ],
    service_account_id: uuid.UUID,
):
    return await service.expire_key(service_account_id, modified_by_id=auth_user.id)
