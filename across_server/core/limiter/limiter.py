from typing import Dict, Sequence, Tuple

import structlog
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from ratelimit import Rule
from ratelimit.auths.ip import client_ip
from ratelimit.auths.jwt import EmptyInformation, create_jwt_auth
from ratelimit.types import ASGIApp, Receive, Scope, Send

from ...auth.config import auth_config
from .config import limiter_config

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

# Create rate limit rules here
# Applies a fixed limit to all routes based on request authorization header jwt "type" as "group"
# Currently 3 group types are supported: "default", "user", "service_account"
# ORDER MATTERS! limit rules are resolved in order by first match
# For more information see https://github.com/abersheeran/asgi-ratelimit
rules: Dict[str, Sequence[Rule]] = {
    r".*/token": [
        Rule(minute=limiter_config.LIMIT_TOKEN_REQUESTS_PER_MINUTE, group="default"),
        Rule(minute=limiter_config.LIMIT_TOKEN_REQUESTS_PER_MINUTE, group="user"),
        Rule(
            minute=limiter_config.LIMIT_TOKEN_REQUESTS_PER_MINUTE,
            group="service_account",
        ),
    ],
    r".*": [
        Rule(minute=limiter_config.LIMIT_DEFAULT_REQUESTS_PER_MINUTE, group="default"),
        Rule(second=limiter_config.LIMIT_USER_REQUESTS_PER_SECOND, group="user"),
        Rule(
            second=limiter_config.LIMIT_SERVICE_ACCOUNT_REQUESTS_PER_SECOND,
            group="service_account",
        ),
    ],
}

jwt_auth = create_jwt_auth(
    auth_config.JWT_SECRET_KEY, auth_config.JWT_ALGORITHM, "sub", "type"
)


async def authenticate_limit(scope: Scope) -> Tuple[str, str]:
    ip: str

    try:
        ip, default = await client_ip(scope)
    except EmptyInformation:
        ip = "unknown"

    user_id: str  # uuid
    group: str  # "user" or "service_account" if jwt, else "default"

    try:
        user_id, group = await jwt_auth(scope)
    except (
        EmptyInformation,
        InvalidSignatureError,
        ExpiredSignatureError,
        DecodeError,
    ):
        user_id = "anonymous"
        group = "default"

    user_limit_key = f"{ip} {user_id}"

    return user_limit_key, group


def on_limit_exceeded(retry_after: int) -> ASGIApp:
    message = "Rate Limit Exceeded."
    try_again_message = f"Try again in {retry_after} seconds."

    async def rate_limit_exceeded(scope: Scope, receive: Receive, send: Send) -> None:
        user_limit_key, group = await authenticate_limit(scope=scope)
        client_ip, access_token_id = user_limit_key.split(" ")

        logger.warning(
            message,
            client_ip=client_ip,
            access_token_id=access_token_id,
            path=scope.get("path"),
            group=group,
        )

        await send(
            {
                "type": "http.response.start",
                "status": 429,
                "content-type": "text",
                "headers": [
                    (b"retry-after", str(retry_after).encode("ascii")),
                    (b"content-type", b"text/plain"),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": f"{message} {try_again_message}".encode("ascii"),
                "more_body": False,
            }
        )

    return rate_limit_exceeded
