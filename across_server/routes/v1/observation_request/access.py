from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends
from fastapi.security import SecurityScopes
from pydantic import BaseModel

from ....auth.schemas import AuthUser
from ....auth.strategies import auth_user_or_none, authenticate_jwt


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
    # service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
    data: Annotated[
        ObservationRequestAccess, Body(title="UUID of the observation request")
    ],
) -> AuthUser:
    """
    This function checks if the authenticated user has access to the specified observation request.
    Will utilize the service layer to query for the observation request and verify if:
    1. the user is the one who created it
    2. the user is a group admin for the instrument's observatory group
    """
    # observation_request = await service.get(observation_request_id=data.observation_request_id)
    return auth_user


async def observation_request_redaction(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser | None, Depends(auth_user_or_none)],
    # service: Annotated[ObservationRequestService, Depends(ObservationRequestService)],
) -> AuthUser | None:
    """
    This function checks if the authenticated user has access to the specified observation request.
    Will utilize the service layer to query for the observation request and verify if:
    1. the user is the one who created it
    2. the user is a group admin for the instrument's observatory group
    """
    # observation_request = await service.get(observation_request_id=data.observation_request_id)
    return auth_user
