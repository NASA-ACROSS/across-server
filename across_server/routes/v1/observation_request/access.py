from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth.schemas import AuthUser
from ....auth.strategies import authenticate_jwt
from ....db import models
from ....db.database import get_session
from .exceptions import ObservationRequestNotFoundException
from .service import _is_admin, _is_creator


async def observation_request_access(
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    observation_request_id: UUID = Path(title="UUID of the observation request"),
) -> AuthUser:
    """
    This function checks if the authenticated user has access to the specified observation request.
    Will utilize the service layer to query for the observation request and verify if:
    1. the user is the one who created it
    2. the user is a group admin for the instrument's observatory group
    """

    is_creator_query = _is_creator(auth_user)
    is_admin_query = _is_admin(auth_user)

    observation_request_exists_query = select(
        models.ObservationRequest,
        or_(is_creator_query, is_admin_query).label("is_creator_or_admin"),
    ).where(models.ObservationRequest.id == observation_request_id)
    result = await db.execute(observation_request_exists_query)
    observation_request_exists, is_creator_or_admin = result.one_or_none() or (
        None,
        False,
    )
    if observation_request_exists is None:
        raise ObservationRequestNotFoundException(
            observation_request_id=observation_request_id
        )

    if is_creator_or_admin:
        return auth_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def observation_request_status_access(
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    observation_request_id: UUID = Path(title="UUID of the observation request"),
) -> AuthUser:
    """
    This function checks if the authenticated user has access to the specified observation request.
    Will utilize the service layer to query for the observation request and verify if:
    1. the user is a group admin for the instrument's observatory group
    """
    is_admin_query = _is_admin(auth_user)

    observation_request_exists_query = select(
        models.ObservationRequest,
        is_admin_query.label("is_admin"),
    ).where(models.ObservationRequest.id == observation_request_id)
    result = await db.execute(observation_request_exists_query)
    observation_request_exists, group_id, is_admin = result.one_or_none() or (
        None,
        None,
        False,
    )
    if observation_request_exists is None:
        raise ObservationRequestNotFoundException(
            observation_request_id=observation_request_id
        )

    if is_admin:
        return auth_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
