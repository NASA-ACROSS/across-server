import secrets
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Path, Request, status
from fastapi.security import SecurityScopes

from .config import auth_config
from .schemas import AuthUser
from .security import extract_creds
from .service import AuthService


async def authenticate(
    service: Annotated[AuthService, Depends(AuthService)],
    token: Annotated[str, Depends(extract_creds)],
) -> AuthUser:
    return await service.authenticate(token)


async def global_access(
    security_scopes: SecurityScopes,
    auth_user: Annotated[AuthUser, Depends(authenticate)],
) -> AuthUser:
    if "all:write" in auth_user.scopes:
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
    auth_user: Annotated[AuthUser, Depends(authenticate)],
) -> AuthUser:
    if "all:write" in auth_user.scopes:
        return auth_user

    for group in auth_user.groups:
        if group.id == group_id and set(security_scopes.scopes).issubset(group.scopes):
            return auth_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


async def self_access(
    user_id: Annotated[UUID, Path(title="UUID of the user")],
    auth_user: Annotated[AuthUser, Depends(authenticate)],
) -> AuthUser:
    if "all:write" in auth_user.scopes:
        return auth_user

    if auth_user.id == user_id:
        return auth_user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied."
    )


async def webserver_access(
    request: Request,
    token: Annotated[str, Depends(extract_creds)],
) -> None:
    is_webserver = secrets.compare_digest(token, auth_config.WEBSERVER_SECRET)

    if request.client:
        ip = str(request.client.host)

    is_ip_allowed = ip in auth_config.ALLOWED_IPS

    if not (is_webserver and is_ip_allowed):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
