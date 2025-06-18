from ...core.config import BaseConfig


class Config(BaseConfig):
    # limit /token route
    LIMIT_TOKEN_REQUESTS_PER_MINUTE: int = 6

    # limit everything else by access type
    LIMIT_DEFAULT_REQUESTS_PER_MINUTE: int = 20
    LIMIT_USER_REQUESTS_PER_SECOND: int = 1
    LIMIT_SERVICE_ACCOUNT_REQUESTS_PER_SECOND: int = 10


limiter_config = Config()
