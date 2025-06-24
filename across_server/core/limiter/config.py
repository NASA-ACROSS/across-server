from collections.abc import Sequence

from ratelimit import Rule

from ...core.config import BaseConfig


class Config(BaseConfig):
    # limit /token route
    LIMIT_TOKEN_REQUESTS_PER_MINUTE: int = 1

    # limit everything else by access type
    LIMIT_DEFAULT_REQUESTS_PER_MINUTE: int = 20
    LIMIT_USER_REQUESTS_PER_SECOND: int = 1
    LIMIT_SERVICE_ACCOUNT_REQUESTS_PER_SECOND: int = 10


limiter_config = Config()

# Create rate limit rules here
# Applies a fixed limit to all routes based on request authorization header jwt "type" as "group"
# Currently 3 group types are supported: "default", "user", "service_account"
# ORDER MATTERS! limit rules are resolved in order by first match
# For more information see https://github.com/abersheeran/asgi-ratelimit
rules: dict[str, Sequence[Rule]] = {
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
