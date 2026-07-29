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
    FRONTEND_HOST: str = "http://localhost:5173"
    PORT: int = 8000
    ROOT_PATH: str = ""

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

    # Always hide local only routes -- mainly used for client generation locally.
    HIDE_LOCAL_ROUTE: bool = True

    DATA_INGESTION_SERVICE_ACCOUNT_ID_PATH: str = "data-ingestion/core-server/client_id"
    DATA_INGESTION_INGESTION_SERVICE_ACCOUNT_SECRET_PATH: str = (
        "data-ingestion/core-server/client_secret"
    )
    FRONTEND_SERVICE_ACCOUNT_ID_PATH: str = "frontend/core-server/client_id"
    FRONTEND_SERVICE_ACCOUNT_SECRET_PATH: str = "frontend/core-server/client_secret"

    APP_TITLE: str = "ACROSS Server"
    APP_SUMMARY: str = "Astrophysics Cross-Observatory Science Support (ACROSS)"
    APP_DESCRIPTION: str = "Server providing tools and utilities for various NASA missions to aid in coordination of large observation efforts."

    # Pagination parameters
    # As of writing, we have ~1.1 million rows in observations table
    # Currently as set allows retrieval up to 2 million results (DEFAULT_PAGE_MAX * DEFAULT_PAGE_LIMIT_MAX)
    DEFAULT_PAGE: int = 1
    DEFAULT_PAGE_MIN: int = 1
    DEFAULT_PAGE_MAX: int = 2000

    DEFAULT_PAGE_LIMIT: int = 100
    DEFAULT_PAGE_LIMIT_MIN: int = 100
    DEFAULT_PAGE_LIMIT_MAX: int = 1000

    def is_local(self) -> bool:
        return self.RUNTIME_ENV == Environments.LOCAL

    def base_url(self) -> str:
        if self.is_local():
            return f"{self.HOST}:{self.PORT}{self.ROOT_PATH}"
        else:
            if self.RUNTIME_ENV == Environments.PRODUCTION:
                return f"https://api.across.sciencecloud.nasa.gov{self.ROOT_PATH}"
            else:
                return f"https://api.{self.RUNTIME_ENV.value}.across.sciencecloud.nasa.gov{self.ROOT_PATH}"


config = Config()
