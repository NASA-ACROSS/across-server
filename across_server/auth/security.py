import datetime
import hashlib
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import auth_config
from .schemas import SecretKeySchema

security = HTTPBearer(
    scheme_name="Authorization",
    description="Enter your access token.",
    auto_error=True,
)


def extract_creds(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> str:
    return credentials.credentials


def generate_secret_key(
    expiration_duration: int = 30, generator_key: str | None = None
) -> SecretKeySchema:
    now = datetime.datetime.now()

    # if I have this defaulted to the config value in the function parameters, it won't be monkey-patched in the unit-tests
    if not generator_key:
        generator_key = auth_config.SERVICE_ACCOUNT_SECRET_KEY

    # Get timestamp in seconds
    timestamp_seconds = now.timestamp()

    # Convert to nanoseconds
    timestamp_nanoseconds = int(timestamp_seconds * 1e9)

    # Construct the salt for the key
    secret_string = generator_key + str(timestamp_nanoseconds)

    return SecretKeySchema(
        key=hashlib.sha512(secret_string.encode()).hexdigest(),
        expiration=now + datetime.timedelta(days=expiration_duration),
    )
