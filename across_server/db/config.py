import boto3
import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

from ..core.config import config as core_config
from ..util.ssm import SSM

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Config(BaseSettings):
    ACROSS_DB_USER: str = "user"
    ACROSS_DB_PWD: str = "local"
    ACROSS_DB_NAME: str = "across"
    ACROSS_DB_HOST: str = "localhost"
    ACROSS_DB_PORT: int = 5432
    ACROSS_DB_ROLE_NAME: str = "across-plat-ue2-dev-DBAccessRole"

    DRIVER_NAME: str = "postgresql+asyncpg"

    _cluster_name: str = (
        f"across-plat-ue2-{core_config.APP_ENV.value.lower()}-core-server-db"
    )

    def DB_URI(self) -> URL:
        if core_config.is_local():
            return self._get_local_uri()
        else:
            return self._get_aurora_uri()

    def _get_ssm_path(self) -> str:
        return f"/aurora-postgres/{self._cluster_name}"

    def _get_local_uri(self) -> URL:
        return URL.create(
            drivername=self.DRIVER_NAME,
            username=self.ACROSS_DB_USER,
            password=self.ACROSS_DB_PWD,
            host=self.ACROSS_DB_HOST,
            port=self.ACROSS_DB_PORT,
            database=self.ACROSS_DB_NAME,
        )

    def _get_aurora_uri(self) -> URL:
        ssm_db_path = self._get_ssm_path()
        cluster_domain = SSM.get_parameter("cluster_domain", ssm_db_path)

        host = "".join([self._cluster_name, ".cluster-", cluster_domain])
        port = int(SSM.get_parameter("db_port", ssm_db_path))
        token = self._get_rds_token(host, port)

        return URL.create(
            drivername=self.DRIVER_NAME,
            username=self.ACROSS_DB_USER,
            password=token,
            host=host,
            port=port,
            database=self.ACROSS_DB_NAME,
        )

    def _get_rds_token(self, host: str, port: int) -> str:
        # Assume DB access Role
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        account_id = identity["Account"]
        username = identity["Arn"].split("/")[-1]
        role_arn = f"arn:aws:iam::{account_id}:role/{self.ACROSS_DB_ROLE_NAME}"
        response = sts.assume_role(RoleArn=role_arn, RoleSessionName=username)

        creds = response["Credentials"]

        # Generate temporary IAM Auth Token
        rds = boto3.client(
            "rds",
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

        return rds.generate_db_auth_token(
            DBHostname=host, Port=port, DBUsername=self.ACROSS_DB_USER
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Config()
