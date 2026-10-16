from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from sqlalchemy import ColumnElement, False_, case, false, select
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth.schemas import AuthUser
from ....auth.strategies import authenticate_jwt
from ....db import models
from ....db.database import get_session
from .exceptions import ObservationRequestNotFoundException


def is_creator_clause(
    auth_user: AuthUser | None,
) -> ColumnElement[bool] | False_:
    if auth_user is None:
        return false()

    return models.ObservationRequest.created_by_id == auth_user.id


def is_writer_clause(
    auth_user: AuthUser | None,
) -> ColumnElement[bool] | False_:
    if auth_user is None:
        return false()

    group_ids = [
        group.id
        for group in auth_user.groups
        if any(
            scope in getattr(group, "scopes", [])
            for scope in [
                "group:all:write",
                "group:observation-request:write",
                "group:observation-request:read",
            ]
        )
    ]

    return models.ObservationRequest.instrument.has(
        models.Instrument.telescope.has(
            models.Telescope.observatory.has(
                models.Observatory.group.has(models.Group.id.in_(group_ids))
            )
        )
    )


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

    observation_request_exists_query = select(
        models.ObservationRequest,
        case(
            (is_writer_clause(auth_user), "writer"),
            (is_creator_clause(auth_user), "creator"),
            else_="viewer",
        ).label("user_type"),
    ).where(models.ObservationRequest.id == observation_request_id)

    exec = await db.execute(observation_request_exists_query)

    res = exec.one_or_none()

    if res is None:
        raise ObservationRequestNotFoundException(
            observation_request_id=observation_request_id
        )

    observation_request_exists, user_type = res

    if observation_request_exists is None:
        raise ObservationRequestNotFoundException(
            observation_request_id=observation_request_id
        )

    if user_type == "viewer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return auth_user


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

    observation_request_exists_query = select(
        models.ObservationRequest,
        is_writer_clause(auth_user).label("is_writer"),
    ).where(models.ObservationRequest.id == observation_request_id)

    result = await db.execute(observation_request_exists_query)

    observation_request, is_writer = result.one_or_none() or (
        None,
        False,
    )

    if observation_request is None:
        raise ObservationRequestNotFoundException(
            observation_request_id=observation_request_id
        )

    if is_writer:
        return auth_user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
