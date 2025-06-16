from ..core.config import BaseConfig


class Config(BaseConfig):
    JWT_SECRET_KEY: str = "SECRET_KEY"
    JWT_MAGIC_LINK_SECRET_KEY: str = "MAGIC_LINK_SECRET_KEY"
    JWT_REFRESH_SECRET_KEY: str = "REFRESH_KEY"
    JWT_ALGORITHM: str = "HS256"
    REFRESH_EXPIRES_IN_DAYS: int = 30
    WEBSERVER_SECRET: str = "WEBSERVER_SECRET_KEY"
    ALLOWED_IPS: list[str] = ["127.0.0.1"]


auth_config = Config()
