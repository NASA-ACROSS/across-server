from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aioboto3
import pytest
import pytest_asyncio
import structlog

from across_server.util.email import config as email_config_module
from across_server.util.email.service import EmailService

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

class MockClientContext:
    """Mimics the async context manager returned by aioboto3 `session.client(...)`."""

    def __init__(self, client: AsyncMock) -> None:
        self._client = client

    async def __aenter__(self) -> AsyncMock:
        return self._client

    async def __aexit__(self, *args: Any) -> None:
        return None


class TestEmailService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, monkeypatch: Any) -> None:
        self.recipient = "mockemail@example.com"
        self.subject = "Mock"

        self.mock_ses_client = AsyncMock()
        self.mock_ses_client.send_raw_email = AsyncMock()

        self.mock_logger = AsyncMock()
        self.mock_logger.warning = MagicMock()
        self.mock_logger.error = MagicMock()

        def fake_session(*args: Any, **kwargs: Any) -> Any:
            session = AsyncMock()
            session.client = lambda *a, **k: MockClientContext(self.mock_ses_client)
            return session

        monkeypatch.setattr(aioboto3, "Session", fake_session)
        monkeypatch.setattr(email_config_module, "logger", self.mock_logger)

    @pytest.mark.asyncio
    async def test_should_not_send_email_when_local(
        self, mock_config_runtime_env_is_local: AsyncMock
    ) -> None:
        """Should not call SES when running locally"""
        mock_config_runtime_env_is_local.return_value = True
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mock_ses_client.send_raw_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_send_email_when_required_data_is_provided(self) -> None:
        """Should send via SES when the required data is provided"""
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mock_ses_client.send_raw_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_throw_error_when_email_fails(self) -> None:
        """Should propagate an error when the SES send fails"""
        self.mock_ses_client.send_raw_email.side_effect = Exception("Mock Exception")
        service = EmailService()
        with pytest.raises(Exception):
            await service.send(recipients=[self.recipient], subject=self.subject)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("recipients", [[], None])
    async def test_should_throw_error_when_missing_recipients(self, recipients) -> None:
        """Should log a warning when sending an email without recipients"""
        service = EmailService()
        await service.send(recipients=recipients, subject=self.subject)
        self.mock_logger.warning.assert_called_once()
        
    @pytest.mark.asyncio
    @pytest.mark.parametrize("subject", ["", None])
    async def test_should_throw_error_when_missing_subject(self, subject) -> None:
        """Should throw an error when sending an email without subject"""
        service = EmailService()
        with pytest.raises(Exception):
            await service.send(recipients=[self.recipient], subject=subject)

    @pytest.mark.asyncio
    async def test_should_skip_send_when_recipient_not_in_restricted_list(
        self, monkeypatch: Any
    ) -> None:
        """Should skip the send when no recipient passes RESTRICTED_TO_EMAIL_LIST"""
        monkeypatch.setattr(
            email_config_module.email_config,
            "RESTRICTED_TO_EMAIL_LIST",
            ["allowed@example.com"],
        )
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mock_ses_client.send_raw_email.assert_not_called()

    @pytest.mark.asyncio
    async def test_should_send_when_recipient_in_restricted_list(
        self, monkeypatch: Any
    ) -> None:
        """Should send when the recipient is on RESTRICTED_TO_EMAIL_LIST"""
        monkeypatch.setattr(
            email_config_module.email_config,
            "RESTRICTED_TO_EMAIL_LIST",
            [self.recipient],
        )
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mock_ses_client.send_raw_email.assert_called_once()
