import structlog
from fastapi import status
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from ratelimit.auths.ip import client_ip
from ratelimit.auths.jwt import EmptyInformation, create_jwt_auth
from ratelimit.types import ASGIApp, Receive, Scope, Send

from ...auth.config import auth_config

type LimitKey = str
type LimitGroup = str

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

jwt_auth = create_jwt_auth(
    auth_config.JWT_SECRET_KEY, auth_config.JWT_ALGORITHM, "sub", "type"
)


async def authenticate_limit(scope: Scope) -> tuple[LimitKey, LimitGroup]:
    ip: str

    try:
        ip, _ = await client_ip(scope)
    except EmptyInformation:
        ip = "unknown"

    user_id: str  # uuid
    limit_group: str  # "user" or "service_account" if jwt, else "default"

    try:
        user_id, limit_group = await jwt_auth(scope)
    except (
        EmptyInformation,
        InvalidSignatureError,
        ExpiredSignatureError,
        DecodeError,
    ):
        user_id = "anonymous"
        limit_group = "default"

    user_limit_key = f"{ip} {user_id}"

    return user_limit_key, limit_group


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
                "status": status.HTTP_429_TOO_MANY_REQUESTS,
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
