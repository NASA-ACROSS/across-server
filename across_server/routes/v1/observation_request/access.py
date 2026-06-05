from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends
from fastapi.security import SecurityScopes
from pydantic import BaseModel

from ....auth.schemas import AuthUser
from ....auth.strategies import authenticate_jwt


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
    return auth_user
