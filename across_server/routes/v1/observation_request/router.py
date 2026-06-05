import datetime
import uuid
from typing import Annotated

from fastapi import APIRouter, Query, Security, status  # Depends

from across_server.auth.strategies import global_access

from ....auth.schemas import AuthUser
from ....core.schemas import Page  # ListResponse
from . import schemas

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
    # service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    observation_request_id: uuid.UUID,
    include_history: Annotated[bool, Query()] = False,
) -> schemas.ObservationRequest:
    # observation_request = await service.get(
    #     observation_request_id, include_history
    # )

    # return schemas.ObservationRequest.from_orm(
    #     observation_request, include_history=include_history
    # )
    return schemas.ObservationRequest(
        id=uuid.uuid4(),
        parent_id=uuid.uuid4(),
        science_justification="Justification",
        object_coordinates=schemas.Coordinate(ra=0.0, dec=0.0),
        observation_window=schemas.NullableEndDateRange(
            begin=datetime.datetime.now(), end=None
        ),
        object_brightness=schemas.UnitValue(value=0.0, unit="mag"),
        object_name="Test Object",
        exposure_time=1000.0,
        anonymize=False,
        is_too=False,
        instrument_id=uuid.uuid4(),
        status=schemas.ObservationRequestStatus.PENDING,
        status_reason="Awaiting review   ",
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
    # service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    data: Annotated[schemas.ObservationRequestReadParams, Query()],
    include_history: Annotated[bool, Query()] = False,
) -> Page[schemas.ObservationRequest]:
    observation_request_tuples = []  # await service.get_many(data=data, include_history=include_history)

    total_number = observation_request_tuples[0][1] if observation_request_tuples else 0

    observation_requests = [tuple[0] for tuple in observation_request_tuples]
    return Page[schemas.ObservationRequest].model_validate(
        {
            "total_number": total_number,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                schemas.ObservationRequest.from_orm(
                    observation_request,
                )
                for observation_request in observation_requests
            ],
        }
    )


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
    auth_user: Annotated[
        AuthUser, Security(global_access, scopes=["observation_request:write"])
    ],
    # service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    data: schemas.ObservationRequestCreate,
) -> uuid.UUID:
    # return await service.create(
    #     observation_request_data=data, created_by_id=auth_user.id
    # )
    return uuid.uuid4()
