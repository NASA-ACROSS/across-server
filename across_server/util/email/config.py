from ...core.config import BaseConfig
from ...core.config import config as core_config
from ...util.ssm import SSM
from aiobotocore.config import AioConfig


def split_list(list_str: str) -> list[str]:
    return [item.strip() for item in list_str.split(",") if item.strip()]


class Config(BaseConfig):
    AWS_SES_REGION: str = "us-east-1"
    AWS_SES_CONFIGURATION_SET: str = "across-no-reply-config-set"
    ACROSS_EMAIL: str = "no-reply@across.sciencecloud.nasa.gov"

    RESTRICTED_TO_EMAIL_LIST: list[str] = []
    ALLOWED_TOP_LEVEL_DOMAINS: list[str] = []

    RESTRICTED_TO_EMAIL_LIST_CSV: str = ""
    ALLOWED_TOP_LEVEL_DOMAINS_CSV: str = ""

    _SES_RETRY_CONFIG = AioConfig(retries={"max_attempts": 4, "mode": "adaptive"})

    def __init__(self) -> None:
        super().__init__()

        self.RESTRICTED_TO_EMAIL_LIST = split_list(self.RESTRICTED_TO_EMAIL_LIST_CSV)

        self.ALLOWED_TOP_LEVEL_DOMAINS = split_list(self.ALLOWED_TOP_LEVEL_DOMAINS_CSV)

        if not core_config.is_local():
            path = f"{core_config.APP_ENV}/core-server"

            self.AWS_SES_REGION = SSM.get_parameter(f"{path}/aws-ses-region")
            self.AWS_SES_CONFIGURATION_SET = SSM.get_parameter(
                f"{path}/ses-configuration-set"
            )
            self.ACROSS_EMAIL = SSM.get_parameter(f"{path}/across-email")
            self.RESTRICTED_TO_EMAIL_LIST = split_list(
                SSM.get_parameter(f"{path}/restricted-to-email-list")
            )
            self.ALLOWED_TOP_LEVEL_DOMAINS = split_list(
                SSM.get_parameter(f"{path}/allowed-top-level-domains")
            )


email_config = Config()
