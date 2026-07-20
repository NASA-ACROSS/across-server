from typing import Annotated
from uuid import UUID

from fastapi import Body, Depends
from fastapi.security import SecurityScopes
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ....auth.schemas import AuthUser
from ....auth.strategies import authenticate_jwt, group_access
from ....db import models
from ....db.database import get_session
from .exceptions import TelescopeNotFoundException


class TelescopeAccess(BaseModel):
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
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
    db: Annotated[AsyncSession, Depends(get_session)],
    data: Annotated[TelescopeAccess, Body(title="UUID of the telescope")],
) -> AuthUser:
    """
    Method that evaluates whether a user has access to a specific telescope

    Parameters
    ----------
    security_scopes: fastapi.SecurityScopes
        list of strings scopes
    auth_user: auth.AuthUser
        an authenticated user retrieved from bearer token
    db: sqlalchemy.ext.asyncio.AsyncSession
        database session
    data: access_schema
        pydantic class that grabs the telescope_id from the request body

    Returns
    -------
    auth_user: auth.AuthUser
        an authenticated user retrieved from bearer token
    """
    query = (
        select(models.Group.id)
        .select_from(models.Telescope)
        .join(models.Telescope.observatory)
        .join(models.Observatory.group)
        .where(models.Telescope.id == data.telescope_id)
    )
    result = await db.execute(query)
    group_id = result.scalar_one_or_none()

    if group_id is None:
        raise TelescopeNotFoundException(data.telescope_id)

    auth_user = await group_access(
        security_scopes=security_scopes, group_id=group_id, auth_user=auth_user
    )
    return auth_user
