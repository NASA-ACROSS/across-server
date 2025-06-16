import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Security, status

from ...auth.schemas import AuthUser
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
    response_model=list[schemas.Schedule],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Schedule],
            "description": "Return a schedule",
        },
    },
)
async def get_many(
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    data: Annotated[schemas.ScheduleRead, Query()],
) -> list[schemas.Schedule]:
    schedules = await service.get_many(data=data)
    return [schemas.Schedule.from_orm(schedule) for schedule in schedules]


@router.get(
    "/history",
    status_code=status.HTTP_200_OK,
    summary="Read schedule(s)",
    description="Read many recent schedules based on query params",
    operation_id="get_history",
    response_model=list[schemas.Schedule],
    responses={
        status.HTTP_200_OK: {
            "model": list[schemas.Schedule],
            "description": "",
        },
    },
)
async def get_history(
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    data: Annotated[schemas.ScheduleRead, Query()],
) -> list[schemas.Schedule]:
    schedules = await service.get_history(data=data)
    return [schemas.Schedule.from_orm(schedule) for schedule in schedules]


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
) -> schemas.Schedule:
    schedule = await service.get(schedule_id)

    return schemas.Schedule.from_orm(schedule)


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
