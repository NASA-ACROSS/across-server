import structlog

from ..core.config import BaseConfig
from ..core.config import config as core_config
from ..util.ssm import SSM

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Config(BaseConfig):
    JWT_SECRET_KEY: str = "SECRET_KEY"
    JWT_MAGIC_LINK_SECRET_KEY: str = "MAGIC_LINK_SECRET_KEY"
    JWT_REFRESH_SECRET_KEY: str = "REFRESH_KEY"
    JWT_ALGORITHM: str = "HS256"
    REFRESH_EXPIRES_IN_DAYS: int = 30
    WEBSERVER_SECRET: str = "WEBSERVER_SECRET_KEY"
    ALLOWED_IPS: list[str] = ["127.0.0.1"]

    def __init__(self) -> None:
        super().__init__()

        if not core_config.is_local():
            self.JWT_SECRET_KEY = SSM.get_parameter(
                f"{core_config.APP_ENV}/core-server/jwt-secret-key"
            )
            self.JWT_MAGIC_LINK_SECRET_KEY = SSM.get_parameter(
                f"{core_config.APP_ENV}/core-server/jwt-magic-link-secret-key"
            )
            self.JWT_REFRESH_SECRET_KEY = SSM.get_parameter(
                f"{core_config.APP_ENV}/core-server/jwt-refresh-secret-key"
            )

            logger.debug(
                "JWT Secrets loaded from SSM Parameter Store",
                jwt_secret_key=bool(self.JWT_SECRET_KEY),
                jwt_magic_link_secret_key=bool(self.JWT_MAGIC_LINK_SECRET_KEY),
                jwt_refresh_secret_key=bool(self.JWT_REFRESH_SECRET_KEY),
            )


auth_config = Config()
