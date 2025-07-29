from typing import TYPE_CHECKING

import boto3
import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL

if TYPE_CHECKING:
    from types_boto3_sts import type_defs as sts

from ..core.config import config as core_config
from ..util.ssm import SSM

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class Config(BaseSettings):
    ACROSS_DB_USER: str = "admin"
    ACROSS_DB_PWD: str = "local"
    ACROSS_DB_NAME: str = "across"
    ACROSS_DB_HOST: str = "localhost"
    ACROSS_DB_PORT: int = 5432
    ACROSS_DB_ROLE_NAME: str = "DBAccessRole"

    DRIVER_NAME: str = "postgresql+asyncpg"

    def __init__(self) -> None:
        super().__init__()

        if core_config.is_local():
            self._uri = self._get_local_uri()
        else:
            self._cluster_name = f"{core_config.APP_ENV}-core-server-db"
            self._ssm_path = f"/aurora-postgres/{self._cluster_name}"
            self._cluster_port = int(SSM.get_parameter("db_port", self._ssm_path))
            cluster_domain = SSM.get_parameter("cluster_domain", self._ssm_path)

            self._cluster_host = "".join(
                [self._cluster_name, ".cluster-", cluster_domain]
            )

            self._uri = self._get_aurora_uri()

    @property
    def DB_URI(self) -> URL:
        return self._uri

    def get_iam_rds_token(self) -> str:
        role = self._assume_role()
        creds = role["Credentials"]

        # Generate temporary IAM Auth Token
        rds = boto3.client(
            "rds",
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
        )

        return rds.generate_db_auth_token(
            DBHostname=self._cluster_host,
            Port=self._cluster_port,
            DBUsername=self.ACROSS_DB_USER,
        )

    def _assume_role(self) -> "sts.AssumeRoleResponseTypeDef":
        sts = boto3.client("sts")
        identity = sts.get_caller_identity()
        account_id = identity["Account"]

        # username is parsed from the end of the ARN
        username = identity["Arn"].split("/")[-1]

        # construct the role ARN
        role_arn = f"arn:aws:iam::{account_id}:role/{core_config.APP_ENV}-{self.ACROSS_DB_ROLE_NAME}"

        return sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=username,
        )

    def _get_aurora_uri(self) -> URL:
        token = self.get_iam_rds_token()

        return URL.create(
            drivername=self.DRIVER_NAME,
            username=self.ACROSS_DB_USER,
            password=token,
            host=self._cluster_host,
            port=self._cluster_port,
            database=self.ACROSS_DB_NAME,
        )

    def _get_local_uri(self) -> URL:
        return URL.create(
            drivername=self.DRIVER_NAME,
            username=self.ACROSS_DB_USER,
            password=self.ACROSS_DB_PWD,
            host=self.ACROSS_DB_HOST,
            port=self.ACROSS_DB_PORT,
            database=self.ACROSS_DB_NAME,
        )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Config()
