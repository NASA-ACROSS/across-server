import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, status

from across_server.core.enums.observation_request_status import ObservationRequestStatus
from across_server.core.schemas.list_response import ListResponse

from ....auth.schemas import AuthUser
from ....auth.strategies import auth_user_or_none, authenticate_jwt
from ....core.schemas import Page  # ListResponse
from . import schemas
from .access import observation_request_access, observation_request_status_access
from .service import ObservationRequestService

router = APIRouter(
    prefix="/observation-request",
    tags=["Observation Request"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The observation request does not exist.",
        },
    },
)


@router.get(
    "/{observation_request_id}",
    summary="Read an observation request",
    description="Read an observation request by its ID.",
    operation_id="get_observation_request",
    status_code=status.HTTP_200_OK,
    response_model=schemas.ObservationRequest,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.ObservationRequest,
            "description": "Return an observation request",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Observation request not found"},
    },
)
async def get(
    auth_user: Annotated[AuthUser | None, Depends(auth_user_or_none)],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    observation_request_id: uuid.UUID,
) -> schemas.ObservationRequest:
    return await service.get(
        observation_request_id=observation_request_id, auth_user=auth_user
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read observation request(s)",
    description="Read most recent observation requests based on query params",
    operation_id="get_observation_requests",
    responses={
        status.HTTP_200_OK: {
            "model": Page[schemas.ObservationRequest],
            "description": "Return observation requests",
        },
    },
)
async def get_many(
    auth_user: Annotated[AuthUser | None, Depends(auth_user_or_none)],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    data: Annotated[schemas.ObservationRequestReadParams, Query()],
) -> Page[schemas.ObservationRequest]:
    observation_requests, total_count = await service.get_many(
        data=data, auth_user=auth_user
    )

    return Page[schemas.ObservationRequest].model_validate(
        {
            "total_number": total_count,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                observation_request for observation_request in observation_requests
            ],
        }
    )


@router.post(
    "/bulk",
    summary="Create many observation requests",
    description="Create new observation requests for ACROSS.",
    operation_id="create_observation_requests_bulk",
    status_code=status.HTTP_201_CREATED,
    response_model=list[uuid.UUID],
    responses={
        status.HTTP_201_CREATED: {
            "model": ListResponse[uuid.UUID],
            "description": "Created observation request ids",
        },
        status.HTTP_409_CONFLICT: {"description": "Duplicate observation request"},
    },
)
async def create_many(
    auth_user: Annotated[AuthUser, Security(authenticate_jwt)],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    data: schemas.ObservationRequestCreateMany,
) -> list[uuid.UUID]:
    return await service.create_many(data=data, created_by_id=auth_user.id)


@router.post(
    "/",
    summary="Create an observation request",
    description="Create a new observation request for ACROSS.",
    operation_id="create_observation_request",
    status_code=status.HTTP_201_CREATED,
    response_model=uuid.UUID,
    responses={
        status.HTTP_201_CREATED: {
            "model": uuid.UUID,
            "description": "Created observation request id",
        },
        status.HTTP_409_CONFLICT: {"description": "Duplicate observation request"},
    },
)
async def create(
    auth_user: Annotated[AuthUser, Security(authenticate_jwt)],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    data: schemas.ObservationRequestCreate,
) -> uuid.UUID:
    return await service.create(data=data, created_by_id=auth_user.id)


@router.put(
    "/{observation_request_id}",
    summary="Update an observation request",
    description="Update an existing observation request for ACROSS.",
    operation_id="update_observation_request",
    status_code=status.HTTP_200_OK,
    response_model=uuid.UUID,
    responses={
        status.HTTP_200_OK: {
            "model": uuid.UUID,
            "description": "Updated observation request id",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Observation request not found"},
    },
)
async def update(
    auth_user: Annotated[
        AuthUser,
        Security(observation_request_access),
    ],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    observation_request_id: uuid.UUID,
    data: schemas.ObservationRequestUpdate,
) -> uuid.UUID:
    return await service.modify(
        observation_request_id=observation_request_id,
        data=data,
        modified_by_id=auth_user.id,
    )


@router.put(
    "/{observation_request_id}/status",
    summary="Update the status of an observation request",
    description="Update the status of an existing observation request for ACROSS.",
    operation_id="update_observation_request_status",
    status_code=status.HTTP_200_OK,
    response_model=uuid.UUID,
    responses={
        status.HTTP_200_OK: {
            "model": uuid.UUID,
            "description": "Updated observation request id",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Observation request not found"},
    },
)
async def update_status(
    auth_user: Annotated[
        AuthUser,
        Security(observation_request_status_access),
    ],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    observation_request_id: uuid.UUID,
    data: schemas.ObservationRequestStatusUpdate,
) -> uuid.UUID:
    return await service.update_status(
        observation_request_id=observation_request_id,
        data=data,
        modified_by_id=auth_user.id,
    )


@router.delete(
    "/{observation_request_id}",
    summary="Delete an observation request",
    description="Delete an existing observation request for ACROSS.",
    operation_id="delete_observation_request",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_204_NO_CONTENT: {
            "description": "Observation request deleted successfully"
        },
        status.HTTP_404_NOT_FOUND: {"description": "Observation request not found"},
    },
)
async def delete(
    auth_user: Annotated[
        AuthUser,
        Security(observation_request_access),
    ],
    service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    observation_request_id: uuid.UUID,
) -> None:
    await service.update_status(
        observation_request_id=observation_request_id,
        data=schemas.ObservationRequestStatusUpdate(
            status=ObservationRequestStatus.ARCHIVED,
            status_reason="Deleted by user",
        ),
        modified_by_id=auth_user.id,
    )
    return None
