from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class Config(BaseSettings):
    ACROSS_DB_USER: str = "user"
    ACROSS_DB_PWD: str = "local"
    ACROSS_DB_NAME: str = "across"
    ACROSS_DB_HOST: str = "localhost"
    ACROSS_DB_PORT: int = 5432

    def DB_URI(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.ACROSS_DB_USER,
            password=self.ACROSS_DB_PWD,
            host=self.ACROSS_DB_HOST,
            port=self.ACROSS_DB_PORT,
            database=self.ACROSS_DB_NAME,
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Config()
