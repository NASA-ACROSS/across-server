import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, status

from ....auth.schemas import AuthUser
from ....core.schemas import ListResponse, Page
from ..telescope.access import telescope_access
from ..telescope.service import TelescopeService
from . import schemas
from .service import ScheduleService

router = APIRouter(
    prefix="/schedule",
    tags=["Schedule"],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "The schedule does not exist.",
        },
    },
)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Read schedule(s)",
    description="Read most recent schedules based on query params",
    operation_id="get_schedules",
    responses={
        status.HTTP_200_OK: {
            "model": Page[schemas.Schedule],
            "description": "Return a schedule",
        },
    },
)
async def get_many(
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    data: Annotated[schemas.ScheduleRead, Query()],
) -> Page[schemas.Schedule]:
    schedule_tuples = await service.get_many(data=data)

    total_number = schedule_tuples[0][1] if schedule_tuples else 0

    schedules = [tuple[0] for tuple in schedule_tuples]
    return Page[schemas.Schedule].model_validate(
        {
            "total_number": total_number,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                schemas.Schedule.from_orm(schedule, data.include_observations)
                for schedule in schedules
            ],
        }
    )


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Read schedule(s)",
    description="Read many recent schedules based on query params",
    operation_id="get_schedules_history",
    responses={
        status.HTTP_200_OK: {
            "model": Page[schemas.Schedule],
            "description": "",
        },
    },
)
async def get_history(
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    data: Annotated[schemas.ScheduleRead, Query()],
) -> Page[schemas.Schedule]:
    schedule_tuples = await service.get_history(data=data)

    total_number = schedule_tuples[0][1] if schedule_tuples else 0

    schedules = [tuple[0] for tuple in schedule_tuples]
    return Page[schemas.Schedule].model_validate(
        {
            "total_number": total_number,
            "page": data.page,
            "page_limit": data.page_limit,
            "items": [
                schemas.Schedule.from_orm(schedule, data.include_observations)
                for schedule in schedules
            ],
        }
    )


@router.get(
    "/{schedule_id}",
    summary="Read a schedule",
    description="Read a schedule by a schedule ID.",
    operation_id="get_schedule",
    status_code=status.HTTP_200_OK,
    response_model=schemas.Schedule,
    responses={
        status.HTTP_200_OK: {
            "model": schemas.Schedule,
            "description": "Return a schedule",
        },
        status.HTTP_404_NOT_FOUND: {"description": "Schedule not found"},
    },
)
async def get(
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    schedule_id: uuid.UUID,
    include_observations: Annotated[bool, Query()] = False,
) -> schemas.Schedule:
    schedule = await service.get(schedule_id)

    return schemas.Schedule.from_orm(schedule, include_observations)


@router.post(
    "/",
    summary="Create a Schedule",
    description="Create a new observing schedule for ACROSS.",
    operation_id="create_schedule",
    status_code=status.HTTP_201_CREATED,
    response_model=uuid.UUID,
    responses={
        status.HTTP_201_CREATED: {
            "model": uuid.UUID,
            "description": "Created schedule id",
        },
        status.HTTP_409_CONFLICT: {"description": "Duplicate schedule"},
    },
)
async def create(
    auth_user: Annotated[
        AuthUser, Security(telescope_access, scopes=["group:schedule:write"])
    ],
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    telescope_service: Annotated[TelescopeService, Depends(TelescopeService)],
    data: schemas.ScheduleCreate,
) -> uuid.UUID:
    telescope = await telescope_service.get(data.telescope_id)
    instruments = telescope.instruments
    return await service.create(
        schedule_create=data, instruments=instruments, created_by_id=auth_user.id
    )


@router.post(
    "/bulk",
    summary="Create many Schedules",
    description="Create many new observing schedules for ACROSS.",
    operation_id="create_many_schedules",
    status_code=status.HTTP_201_CREATED,
    response_model=ListResponse[uuid.UUID],
    responses={
        status.HTTP_201_CREATED: {
            "model": ListResponse[uuid.UUID],
            "description": "Created schedule ids",
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Incorrect schedule parameters"
        },
    },
)
async def create_many(
    auth_user: Annotated[
        AuthUser, Security(telescope_access, scopes=["group:schedule:write"])
    ],
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    telescope_service: Annotated[TelescopeService, Depends(TelescopeService)],
    data: schemas.ScheduleCreateMany,
) -> list[uuid.UUID]:
    telescope = await telescope_service.get(data.telescope_id)
    instruments = telescope.instruments

    return await service.create_many(
        schedule_create_many=data,
        instruments=instruments,
        created_by_id=auth_user.id,
    )
