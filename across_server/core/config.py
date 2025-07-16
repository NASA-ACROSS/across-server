from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import Environments


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Config(BaseConfig):
    # this is auto-populated from infrastructure deployments and used to match naming convention for resources.
    APP_ENV: str = "across-plat-lcl-local"
    RUNTIME_ENV: Environments = Environments.LOCAL
    # need http:// prefix to prevent href removal in some email clients
    HOST: str = "http://localhost"
    PORT: int = 8000
    ROOT_PATH: str = "/api"

    SERVICE_ACCOUNT_EXPIRATION_DURATION: int = 30

    # AWS Configuration
    AWS_REGION: str = "us-east-2"
    AWS_PROFILE: str | None = None

    # Logging
    LOG_LEVEL: str = "DEBUG"
    # Adjusts the output being rendered as JSON (False for dev with pretty-print).
    LOG_JSON_FORMAT: bool = False

    # Request Headers
    REQUEST_ID_HEADER: str = "X-Request-ID"

    def is_local(self) -> bool:
        return self.RUNTIME_ENV == Environments.LOCAL

    def base_url(self) -> str:
        return f"{self.HOST}:{self.PORT}{self.ROOT_PATH}"


config = Config()
