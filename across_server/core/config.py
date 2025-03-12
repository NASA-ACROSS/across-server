from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import Environments


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Config(BaseConfig):
    APP_ENV: Environments = Environments.LOCAL
    HOST: str = "localhost"
    PORT: int = 8000
    ROOT_PATH: str = "/api"

    SERVICE_ACCOUNT_EXPIRATION_DURATION: int = 30

    # Logging
    LOG_LEVEL: str = "DEBUG"
    # Adjusts the output being rendered as JSON (False for dev with pretty-print).
    LOG_JSON_FORMAT: bool = False

    # Request Headers
    REQUEST_ID_HEADER: str = "X-Request-ID"

    def is_local(self) -> bool:
        return self.APP_ENV == Environments.LOCAL

    def base_url(self) -> str:
        return f"{self.HOST}:{self.PORT}{self.ROOT_PATH}"


config = Config()
