import os
from collections.abc import Generator
from unittest.mock import MagicMock, patch

import pytest
from botocore.exceptions import ClientError

from across_server.core.config import config
from across_server.core.enums import Environments
from across_server.util.ssm import SSM


@pytest.fixture
def mock_ssm_client() -> Generator[MagicMock]:
    with patch("boto3.client") as mock_client:
        yield mock_client


class TestSSM:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        # Reset the client before each test
        SSM._client = None

    def test_get_parameter_local_environment(self) -> None:
        """Test parameter retrieval in local environment using env vars"""
        with patch.object(config, "APP_ENV", Environments.LOCAL):
            with patch.dict(os.environ, {"TEST_PARAM": "test_value"}):
                value = SSM.get_parameter("TEST_PARAM")
                assert value == "test_value"

    def test_get_parameter_local_environment_missing(self) -> None:
        """Test parameter retrieval in local environment when env var is missing"""
        with patch.object(config, "APP_ENV", Environments.LOCAL):
            with patch.dict(os.environ, clear=True):
                value = SSM.get_parameter("MISSING_PARAM")
                assert value == ""

    def test_get_parameter_non_local_no_region(self) -> None:
        """Test parameter retrieval fails when AWS_REGION is not set in non-local environment"""
        with patch.object(config, "APP_ENV", Environments.PRODUCTION):
            with patch.object(config, "AWS_REGION", None):
                with pytest.raises(ValueError, match="AWS_REGION must be set"):
                    SSM.get_parameter("TEST_PARAM")

    def test_get_parameter_non_local_success(self, mock_ssm_client: MagicMock) -> None:
        """Test successful parameter retrieval from AWS Parameter Store"""
        mock_client = MagicMock()
        mock_client.get_parameter.return_value = {"Parameter": {"Value": "test_value"}}
        mock_ssm_client.return_value = mock_client

        with patch.object(config, "APP_ENV", Environments.PRODUCTION):
            with patch.object(config, "AWS_REGION", "us-east-2"):
                SSM.get_parameter("TEST_PARAM")

                mock_client.get_parameter.assert_called_once_with(
                    Name="/TEST_PARAM", WithDecryption=True
                )

    def test_get_parameter_custom_path(self, mock_ssm_client: MagicMock) -> None:
        """Test parameter retrieval with custom path"""
        mock_client = MagicMock()
        mock_client.get_parameter.return_value = {"Parameter": {"Value": "test_value"}}
        mock_ssm_client.return_value = mock_client

        with patch.object(config, "APP_ENV", Environments.PRODUCTION):
            with patch.object(config, "AWS_REGION", "us-east-2"):
                SSM.get_parameter("TEST_PARAM", path="/custom/path")

                mock_client.get_parameter.assert_called_once_with(
                    Name="/custom/path/TEST_PARAM", WithDecryption=True
                )

    def test_get_parameter_not_found(self, mock_ssm_client: MagicMock) -> None:
        """Test parameter not found in AWS Parameter Store"""
        mock_client = MagicMock()
        mock_client.exceptions.ParameterNotFound = ClientError
        mock_client.get_parameter.side_effect = ClientError(
            {"Error": {"Code": "ParameterNotFound"}}, "GetParameter"
        )
        mock_ssm_client.return_value = mock_client

        with patch.object(config, "APP_ENV", Environments.PRODUCTION):
            with patch.object(config, "AWS_REGION", "us-east-2"):
                with pytest.raises(ValueError, match="Parameter .* not found"):
                    SSM.get_parameter("MISSING_PARAM")

    def test_get_parameter_no_value(self, mock_ssm_client: MagicMock) -> None:
        """Test parameter exists but has no value"""
        mock_client = MagicMock()
        mock_client.get_parameter.return_value = {"Parameter": {}}  # No Value key
        mock_ssm_client.return_value = mock_client

        with patch.object(config, "APP_ENV", Environments.PRODUCTION):
            with patch.object(config, "AWS_REGION", "us-east-2"):
                with pytest.raises(ValueError, match="Parameter .* has no value"):
                    SSM.get_parameter("INVALID_PARAM")
