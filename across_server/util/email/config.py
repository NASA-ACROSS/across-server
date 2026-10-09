from aiobotocore.config import AioConfig

from ...core.config import BaseConfig
from ...core.config import config as core_config
from ...util.ssm import SSM


def split_list(list_str: str) -> list[str]:
    return [item.strip() for item in list_str.split(",") if item.strip()]


SSM_PATH = path = f"{core_config.APP_ENV}/core-server"


class Config(BaseConfig):
    AWS_SES_REGION: str = "us-east-1"
    AWS_SES_CONFIGURATION_SET: str = "across-no-reply-config-set"
    ACROSS_EMAIL: str = "no-reply@across.sciencecloud.nasa.gov"

    RESTRICTED_TO_EMAIL_LIST_CSV: str = ""
    ALLOWED_TOP_LEVEL_DOMAINS_CSV: str = ""

    _SES_RETRY_CONFIG = AioConfig(retries={"max_attempts": 4, "mode": "adaptive"})

    def __init__(self) -> None:
        super().__init__()

        if core_config.is_local():
            return

        self.AWS_SES_REGION = SSM.get_parameter(f"{SSM_PATH}/aws-ses-region")
        self.AWS_SES_CONFIGURATION_SET = SSM.get_parameter(
            f"{SSM_PATH}/ses-configuration-set"
        )
        self.ACROSS_EMAIL = SSM.get_parameter(f"{SSM_PATH}/across-email")

    @property
    def RESTRICTED_TO_EMAIL_LIST(self) -> list[str]:
        if core_config.is_local():
            return split_list(self.RESTRICTED_TO_EMAIL_LIST_CSV)

        return split_list(SSM.get_parameter(f"{SSM_PATH}/restricted-to-email-list"))

    @property
    def ALLOWED_TOP_LEVEL_DOMAINS(self) -> list[str]:
        if core_config.is_local():
            return split_list(self.ALLOWED_TOP_LEVEL_DOMAINS_CSV)

        return split_list(SSM.get_parameter(f"{SSM_PATH}/allowed-top-level-domains"))


email_config = Config()
