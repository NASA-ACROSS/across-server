import os
from typing import TYPE_CHECKING

import boto3

if TYPE_CHECKING:
    from types_boto3_ssm import SSMClient

from ..core.config import config


class SSM:
    """Utility class to interact with AWS Systems Manager Parameter Store"""

    _client: "SSMClient | None" = None

    @classmethod
    def _get_client(cls) -> "SSMClient":
        if cls._client is None:
            if not config.AWS_REGION:
                raise ValueError("AWS_REGION must be set in non-local environments")

            cls._client = boto3.client("ssm", region_name=config.AWS_REGION)

        return cls._client

    @classmethod
    def get_parameter(cls, name: str, path: str = "") -> str:
        """Get a parameter from AWS Parameter Store or environment variable.

        Args:
            name: The name of the parameter to get
            path: The parameter path prefix (default: "/")

        Returns:
            The parameter value

        Raises:
            ValueError: If the parameter is not found, has no value, or AWS_REGION is not set in non-local environments
        """
        if config.is_local():
            return os.getenv(name, "")

        client = cls._get_client()
        param_name = f"{path}/{name}" if len(path) > 0 else f"/{name}"
        param_value = None

        try:
            response = client.get_parameter(Name=param_name, WithDecryption=True)
            param_value = response.get("Parameter", {}).get("Value")

        except client.exceptions.ParameterNotFound:
            raise ValueError(f"Parameter {param_name} not found in AWS Parameter Store")

        if param_value is None:
            raise ValueError(
                f"Parameter {param_name} has no value in AWS Parameter Store"
            )

        return param_value
