import datetime
import secrets
from typing import Annotated

from fastapi import Depends, Form, HTTPException, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)

from .schemas import AuthUser, GrantType, SecretKeySchema
from .service import AuthService

bearer_dependency = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your access token.",
    auto_error=False,
)

client_credentials_dependency = HTTPBasic(
    scheme_name="Service Account Authorization",
    description="Enter your client credentials.",
    auto_error=False,
)


def bearer_security(
    bearer_credentials: Annotated[
        HTTPAuthorizationCredentials, Depends(bearer_dependency)
    ],
) -> str | None:
    if not bearer_credentials:
        return None
    return bearer_credentials.credentials


def client_credentials_security(
    client_credentials: Annotated[
        HTTPBasicCredentials, Depends(client_credentials_dependency)
    ],
) -> HTTPBasicCredentials | None:
    if not client_credentials:
        return None
    return client_credentials


async def authenticate_grant_type(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    bearer_credentials: Annotated[str, Depends(bearer_security)],
    client_credentials: Annotated[
        HTTPBasicCredentials, Depends(client_credentials_security)
    ],
    grant_type: Annotated[GrantType, Form()],
) -> AuthUser | None:
    if not (bearer_credentials or client_credentials) or grant_type is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if bearer_credentials is not None and grant_type == GrantType.JWT:
        auth_user = await auth_service.authenticate_user(bearer_credentials)
        return auth_user
    elif client_credentials is not None and grant_type == GrantType.CLIENT_CREDENTIALS:
        auth_user = await auth_service.authenticate_service_account(client_credentials)
        return auth_user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def generate_secret_key(expiration_duration: int = 30) -> SecretKeySchema:
    now = datetime.datetime.now()

    return SecretKeySchema(
        key=secrets.token_hex(64),
        salt=secrets.token_hex(64),
        expiration=now + datetime.timedelta(days=expiration_duration),
    )
