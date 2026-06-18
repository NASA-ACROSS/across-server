from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import SecurityScopes

from .schemas import AuthUser
from .security import (
    get_bearer_credentials,
)
from .service import AuthService


async def authenticate(
    service: Annotated[AuthService, Depends(AuthService)],
    token: Annotated[str, Depends(get_bearer_credentials)],
) -> AuthUser:
    return await service.authenticate_user(token)


async def authenticate_jwt(
    service: Annotated[AuthService, Depends(AuthService)],
    token: Annotated[str, Depends(get_bearer_credentials)],
) -> AuthUser:
    return await service.authenticate_jwt(token)


async def global_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
) -> AuthUser:
    if system_access(auth_user):
        return auth_user

    for scope in security_scopes.scopes:
        if scope not in auth_user.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
                headers={
                    "WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'
                },
            )

    return auth_user


async def group_access(
    security_scopes: SecurityScopes,
    group_id: Annotated[UUID, Path(title="UUID of the group")],
    auth_user: Annotated[AuthUser, Depends(authenticate_jwt)],
) -> AuthUser:
    if system_access(auth_user):
        return auth_user

    for group in auth_user.groups:
        # check if group.scopes has admin group:write
        is_admin = "group:all:write" in group.scopes
        has_permission = set(security_scopes.scopes).issubset(group.scopes)
        user_is_in_group = group.id == group_id

        if user_is_in_group:
            if is_admin or has_permission:
                return auth_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


def system_access(principal: AuthUser) -> bool:
    system_scopes = [scope for scope in principal.scopes if scope.startswith("system")]

    return len(system_scopes) > 0


async def self_access(
    _: SecurityScopes,
    user_id: Annotated[UUID, Path(title="UUID of the user")],
    auth_user: Annotated[AuthUser, Depends(authenticate)],
) -> AuthUser:
    if system_access(auth_user):
        return auth_user

    if auth_user.id == user_id:
        return auth_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


async def system_service_account_access(
    _: SecurityScopes,
    service_account_id: Annotated[UUID, Path(title="UUID of the service account")],
    principal: Annotated[AuthUser, Depends(authenticate_jwt)],
) -> AuthUser:
    is_system = system_access(principal)

    if is_system and principal.id == service_account_id:
        return principal

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


async def webserver_access(
    security_scopes: SecurityScopes,
    webserver: Annotated[AuthUser, Depends(authenticate_jwt)],
) -> AuthUser:
    """
    Dependency to authenticate the frontend service account.
    """

    is_system = system_access(webserver)
    has_scopes = set(security_scopes.scopes).issubset(webserver.scopes)

    if is_system and has_scopes:
        return webserver

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden",
    )
