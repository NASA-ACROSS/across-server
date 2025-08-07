from typing import Annotated

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)

from .enums import GrantType
from .schemas import AuthUser
from .service import AuthService

http_bearer = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your access token.",
    auto_error=False,
)

http_basic = HTTPBasic(
    scheme_name="Service Account Authorization",
    description="Enter your client credentials.",
    auto_error=False,
)


def get_bearer_credentials(
    bearer: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
) -> str | None:
    if not bearer:
        return None
    return bearer.credentials


def get_basic_credentials(
    basic_credentials: Annotated[HTTPBasicCredentials, Depends(http_basic)],
) -> HTTPBasicCredentials | None:
    if not basic_credentials:
        return None
    return basic_credentials


async def authenticate_grant_type(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    bearer_credentials: Annotated[str, Depends(get_bearer_credentials)],
    client_credentials: Annotated[HTTPBasicCredentials, Depends(get_basic_credentials)],
    grant_type: Annotated[GrantType, Form()],
) -> AuthUser | None:
    if bearer_credentials and grant_type == GrantType.JWT:
        auth_user = await auth_service.authenticate_user(bearer_credentials)
        return auth_user
    elif client_credentials and grant_type == GrantType.CLIENT_CREDENTIALS:
        auth_user = await auth_service.authenticate_service_account(client_credentials)
        return auth_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
