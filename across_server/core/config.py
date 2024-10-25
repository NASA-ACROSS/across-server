from pydantic_settings import BaseSettings, SettingsConfigDict

from .enums import Environments


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class Config(BaseConfig):
    APP_ENV: Environments = Environments.LOCAL
    HOST: str = "localhost"
    PORT: int = 8000
    ROOT_PATH: str = "/api"

    def is_local(self):
        return self.APP_ENV == Environments.LOCAL

    def base_url(self):
        return f"{self.HOST}:{self.PORT}{self.ROOT_PATH}"


config = Config()
