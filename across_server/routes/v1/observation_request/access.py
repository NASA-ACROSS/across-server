from typing import Annotated
from uuid import UUID

from fastapi import Depends, Path
from fastapi.security import SecurityScopes
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth.schemas import AuthUser
from ....auth.strategies import authenticate_jwt
from ....core.exceptions import AcrossHTTPException  # replace with valid exception
from ....db import models
from ....db.database import get_session


class ObservationRequestAccess(BaseModel):
    """
    A Pydantic model class representing the access to an Observation Request

    Parameters
    ----------
    observation_request_id : UUID
        Record identifier for the observation request

    """

    observation_request_id: UUID


async def observation_request_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    data: Annotated[
        ObservationRequestAccess, Path(title="UUID of the observation request")
    ],
) -> AuthUser:
    """
    This function checks if the authenticated user has access to the specified observation request.
    Will utilize the service layer to query for the observation request and verify if:
    1. the user is the one who created it
    2. the user is a group admin for the instrument's observatory group
    """
    query = (
        select(models.Group.id, models.ObservationRequest.created_by_id)
        .select_from(models.ObservationRequest)
        .join(models.ObservationRequest.instrument)
        .join(models.Instrument.telescope)
        .join(models.Telescope.observatory)
        .join(models.Observatory.group)
        .where(models.ObservationRequest.id == data.observation_request_id)
    )
    result = await db.execute(query)
    row = result.one_or_none()
    if row is None:
        raise AcrossHTTPException(
            status_code=404, message="Observation request not found", log_data={}
        )
    group_id, created_by_id = row

    if auth_user.id == created_by_id or any(
        group.id == group_id for group in auth_user.groups
    ):  # if group.is_admin):
        return auth_user

    raise AcrossHTTPException(
        status_code=401,
        message="Unauthorized access to observation request",
        log_data={},
    )


async def observation_request_status_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    data: Annotated[
        ObservationRequestAccess, Path(title="UUID of the observation request")
    ],
) -> AuthUser:
    """
    This function checks if the authenticated user has access to the specified observation request.
    Will utilize the service layer to query for the observation request and verify if:
    1. the user is the one who created it
    2. the user is a group admin for the instrument's observatory group
    """
    query = (
        select(models.Group.id)
        .select_from(models.ObservationRequest)
        .join(models.ObservationRequest.instrument)
        .join(models.Instrument.telescope)
        .join(models.Telescope.observatory)
        .join(models.Observatory.group)
        .where(models.ObservationRequest.id == data.observation_request_id)
    )
    result = await db.execute(query)
    row = result.one_or_none()
    if row is None:
        raise AcrossHTTPException(
            status_code=404, message="Observation request not found", log_data={}
        )
    (group_id,) = row

    if any(group.id == group_id for group in auth_user.groups):  # if group.is_admin):
        return auth_user

    raise AcrossHTTPException(
        status_code=401,
        message="Unauthorized access to observation request",
        log_data={},
    )
