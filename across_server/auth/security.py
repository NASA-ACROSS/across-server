import datetime
import hashlib
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import auth_config

security = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your access token.",
    auto_error=True,
)


def extract_creds(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    return credentials.credentials


def generate_secret_key() -> str:
    now = datetime.datetime.now()

    # Get timestamp in seconds
    timestamp_seconds = now.replace(tzinfo=datetime.timezone.utc).timestamp()

    # Convert to nanoseconds
    timestamp_nanoseconds = int(timestamp_seconds * 1e9)

    secret_string = auth_config.SERVICE_ACCOUNT_SECRET_KEY + str(timestamp_nanoseconds)

    return hashlib.sha512(secret_string.encode()).hexdigest()
