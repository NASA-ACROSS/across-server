from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your access token.",
    auto_error=True,
)


def extract_creds(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    return credentials.credentials
