from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends
from fastapi.security import SecurityScopes
from pydantic import BaseModel

from ...auth.schemas import AuthUser
from ...auth.strategies import authenticate, group_access
from .service import InstrumentService


class InstrumentAccess(BaseModel):
    """
    A Pydantic model class representing the access to a Instrument
    Parameters
    ----------
    instrument_id : UUID
        Record identifier for the instrument
    """

    instrument_id: UUID


async def instrument_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate)],
    service: Annotated[InstrumentService, Depends(InstrumentService)],
    data: Annotated[InstrumentAccess, Body(title="UUID of the instrument")],
):
    """
    Method that evaluates whether a user has access to a specific instrument

    Parameters
    ----------
    security_scopes: fastapi.SecurityScopes
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
    instrument = await service.get(instrument_id=data.instrument_id)

    group_id = str(instrument.telescope.observatory.group.id)

    auth_user = await group_access(
        security_scopes=security_scopes, group_id=group_id, auth_user=auth_user
    )
    return auth_user
