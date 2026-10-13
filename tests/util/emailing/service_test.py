from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aioboto3
import pytest
import pytest_asyncio
import structlog
from fastapi import HTTPException

import across_server.util.email.service as email_service_module
from across_server.util.email import config as email_config_module
from across_server.util.email.service import EmailService

logger: structlog.stdlib.BoundLogger = structlog.get_logger()


class MockClientContext:
    """Mimics the async context manager returned by aioboto3 `session.client(...)`."""

    def __init__(self, client: AsyncMock) -> None:
        self._client = client

    async def __aenter__(self) -> AsyncMock:
        return self._client

    async def __aexit__(self, *_: Any) -> None:
        return None


class TestEmailService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, monkeypatch: Any, mock_email_config: MagicMock) -> None:
        self.recipient = "mockemail@example.com"
        self.subject = "Mock"

        # force the restricted list to include the mock recipient
        mock_email_config.RESTRICTED_TO_EMAIL_LIST = ["mockemail@example.com"]

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
        monkeypatch.setattr(email_service_module, "logger", self.mock_logger)

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
        with pytest.raises(Exception) as _:
            await service.send(recipients=[self.recipient], subject=self.subject)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("recipients", [[], None])
    async def test_should_throw_error_when_missing_recipients(
        self, recipients: list[str] | None
    ) -> None:
        """Should log a warning when sending an email without recipients"""
        service = EmailService()
        with pytest.raises(Exception) as _:
            await service.send(recipients=recipients or [], subject=self.subject)
        self.mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("subject", ["", None])
    async def test_should_send_email_on_empty_subject(
        self, subject: str | None
    ) -> None:
        """Should send an email even when the subject is empty"""
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=subject or "")
        self.mock_ses_client.send_raw_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_raise_403_exception_when_recipient_not_in_restricted_to_list(
        self, mock_email_config: MagicMock
    ) -> None:
        """Should raise exception when attempting to send when no recipient passes RESTRICTED_TO_EMAIL_LIST"""
        mock_email_config.RESTRICTED_TO_EMAIL_LIST = ["allowed@example.com"]
        service = EmailService()
        with pytest.raises(HTTPException) as exc_info:
            await service.send(recipients=[self.recipient], subject=self.subject)
        assert exc_info.value.status_code == 403

    @pytest.mark.asyncio
    async def test_should_log_error_when_recipient_not_in_restricted_to_list(
        self, mock_email_config: MagicMock
    ) -> None:
        """Should log an error when attempting to send when no recipient passes RESTRICTED_TO_EMAIL_LIST"""
        mock_email_config.RESTRICTED_TO_EMAIL_LIST = ["allowed@example.com"]
        service = EmailService()
        with pytest.raises(Exception) as _:
            await service.send(recipients=[self.recipient], subject=self.subject)
        self.mock_logger.error.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_send_when_recipient_in_restricted_list(self) -> None:
        """Should send when the recipient is on RESTRICTED_TO_EMAIL_LIST"""
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mock_ses_client.send_raw_email.assert_called_once()
