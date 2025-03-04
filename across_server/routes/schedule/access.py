from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends
from fastapi.security import SecurityScopes
from pydantic import BaseModel

from ...auth.schemas import AuthUser
from ...auth.strategies import authenticate, group_access
from .service import ScheduleService


class ScheduleAccess(BaseModel):
    """
    A Pydantic model class representing the access to a Schedule

    Parameters
    ----------
    schedule_id : UUID
        Record identifier for a Schedule

    """

    schedule_id: UUID


async def schedule_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate)],
    service: Annotated[ScheduleService, Depends(ScheduleService)],
    data: Annotated[ScheduleAccess, Body(title="UUID of the schedule")],
):
    """
    Method that evaluates whether a user has access to a specific Schedule for a group

    Parameters
    ----------
    security_scopes: fastapi.security.SecurityScopes
        list of strings scopes
    auth_user: auth.AuthUser
        an authenticated user retrieved from bearer token
    service: ScheduleService
        pydantic schedule service class, allowing db access
    data: access_schema
        pydantic class that grabs the schedule_id from the request body

    Returns
    -------
    auth_user: auth.AuthUser
        an authenticated user retrieved from bearer token
    """
    schedule = await service.get(schedule_id=data.schedule_id)

    group_id = str(schedule.telescope.observatory.group.id)

    auth_user = await group_access(
        security_scopes=security_scopes, group_id=group_id, auth_user=auth_user
    )
    return auth_user
