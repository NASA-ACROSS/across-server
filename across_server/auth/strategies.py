import secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.security import SecurityScopes

from .config import auth_config
from .schemas import AuthUser
from .security import get_bearer_credentials
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
    auth_user: Annotated[AuthUser, Depends(authenticate)],
) -> AuthUser:
    if system_access(security_scopes, auth_user):
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
    if system_access(security_scopes, auth_user):
        return auth_user

    for group in auth_user.groups:
        if group.id == group_id and set(security_scopes.scopes).issubset(group.scopes):
            return auth_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


def system_access(security_scopes: SecurityScopes, principal: AuthUser) -> bool:
    system_scopes = [
        scope for scope in security_scopes.scopes if scope.startswith("system")
    ]

    # verify against the principal's scopes
    # if the system scopes are a subset of the
    # principal scopes, the system has access.
    return set(system_scopes).issubset(principal.scopes)


async def self_access(
    security_scopes: SecurityScopes,
    user_id: Annotated[UUID, Path(title="UUID of the user")],
    auth_user: Annotated[AuthUser, Depends(authenticate)],
) -> AuthUser:
    if system_access(security_scopes, auth_user):
        return auth_user

    if auth_user.id == user_id:
        return auth_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


async def system_service_account_access(
    security_scopes: SecurityScopes,
    service_account_id: Annotated[UUID, Path(title="UUID of the service account")],
    principal: Annotated[AuthUser, Depends(authenticate_jwt)],
) -> AuthUser:
    is_system = system_access(security_scopes, principal)

    if is_system and principal.id == service_account_id:
        return principal

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


async def webserver_access(
    request: Request,
    token: Annotated[str, Depends(get_bearer_credentials)],
) -> None:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    is_webserver = secrets.compare_digest(token, auth_config.WEBSERVER_SECRET)

    if request.client:
        ip = str(request.client.host)

    is_ip_allowed = ip in auth_config.ALLOWED_IPS

    if not (is_webserver and is_ip_allowed):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
