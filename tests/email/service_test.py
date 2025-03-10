from unittest.mock import AsyncMock

import aiosmtplib
import pytest
import pytest_asyncio

from across_server.util.email.service import EmailService


class TestEmailService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, monkeypatch):
        self.recipient = "mockemail"
        self.subject = "Mock"

        class mocksmtp(aiosmtplib.SMTP):
            is_connected: bool = True

            async def login(*args, **kwargs):
                pass

            async def sendmail(*args, **kwargs):
                pass

        mock_sendmail = AsyncMock()  # Need to mock to assert it gets called
        monkeypatch.setattr(mocksmtp, "sendmail", mock_sendmail)
        monkeypatch.setattr(aiosmtplib, "SMTP", mocksmtp)

        self.mocksmtp = mocksmtp

    @pytest.mark.asyncio
    async def test_should_send_email_when_required_data_is_provided(self):
        """Should send an email when the required data is provided"""
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mocksmtp.sendmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_throw_error_when_email_fails(self):
        """
        Should throw an error when sending an email fails
        """
        self.mocksmtp.sendmail.side_effect = Exception("Mock Exception")
        service = EmailService()
        with pytest.raises(Exception):
            await service.send(recipients=[self.recipient], subject=self.subject)

    @pytest.mark.asyncio
    async def test_should_throw_error_when_missing_recipients(self):
        """Should throw an error when sending an email without recipients"""
        service = EmailService()
        with pytest.raises(Exception):
            await service.send(subject=self.subject)  # type: ignore

    @pytest.mark.asyncio
    async def test_should_throw_error_when_missing_subject(self):
        """Should throw an error when sending an email without subject"""
        service = EmailService()
        with pytest.raises(Exception):
            await service.send(recipients=[self.recipient])  # type: ignore
