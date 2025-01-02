import uuid
from typing import Annotated, List

from fastapi import APIRouter, Depends, status

from ... import auth, db
from . import schemas
from .service import UserService

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The user does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[schemas.User],
)
async def get_many(service: Annotated[UserService, Depends(UserService)]):
    return await service.get_many()


@router.get(
    "/{user_id}",
    summary="Read a user",
    description="Read a user by a user ID.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "Return a user",
        },
    },
    dependencies=[Depends(auth.strategies.self_access)],
)
async def get(
    service: Annotated[UserService, Depends(UserService)], user_id: uuid.UUID
):
    return await service.get(user_id)


@router.post(
    "/",
    summary="Create a user",
    description="Create a new user for ACROSS.",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.User,
    responses={
        status.HTTP_201_CREATED: {
            "model": schemas.User,
            "description": "The newly created user",
        },
    },
)
async def create(
    service: Annotated[UserService, Depends(UserService)],
    data: schemas.UserCreate,
):
    return await service.create(data)


@router.patch(
    "/{user_id}",
    summary="Update a user",
    description="Update a user's information for the allowed properties.",
    status_code=status.HTTP_200_OK,
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "The updated user",
        },
    },
)
async def update(
    auth_user: Annotated[db.models.User, Depends(auth.strategies.self_access)],
    service: Annotated[UserService, Depends(UserService)],
    user_id: uuid.UUID,
    data: schemas.UserUpdate,
):
    return await service.update(user_id, data, modified_by=auth_user)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    description="Permanently delete a user from the ACROSS system. This will also delete all associated relations for the user.",
    response_model=schemas.User,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.User,
            "description": "Upon successful deletion, the user is returned",
        },
    },
)
async def delete(
    service: Annotated[UserService, Depends(UserService)],
    user_id: uuid.UUID,
):
    return await service.delete(user_id)
