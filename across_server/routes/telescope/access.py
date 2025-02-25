from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends
from fastapi.security import SecurityScopes
from pydantic import BaseModel

from ...auth.schemas import AuthUser
from ...auth.strategies import authenticate, group_access
from .service import TelescopeService


class access_schema(BaseModel):
    """
    A Pydantic model class representing the access to a Telescope

    Parameters
    ----------
    telescope_id : UUID
        Record identifier for the telescope

    """

    telescope_id: UUID


async def telescope_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate)],
    service: Annotated[TelescopeService, Depends(TelescopeService)],
    data: Annotated[access_schema, Body(title="UUID of the group")],
):
    """
    Method that evaluates whether a user has access to a specific telescope

    Parameters
    ----------
    security_scoopes: fastapi.SecurityScopes
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
    telescope = await service.get(telescope_id=data.telescope_id)

    group_id = str(telescope.observatory.group.id)

    auth_user = await group_access(
        security_scopes=security_scopes, group_id=group_id, auth_user=auth_user
    )
    return auth_user
