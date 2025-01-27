import smtplib
from unittest.mock import Mock

import pytest
import pytest_asyncio

from across_server.util.email.service import EmailService


class TestEmailService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, monkeypatch):
        self.recipient = "mockemail"
        self.subject = "Mock"

        class mocksmtp(smtplib.SMTP_SSL):
            def login(*args, **kwargs):
                pass

            def sendmail(*args, **kwargs):
                pass

        mock_sendmail = Mock()  # Need to mock to assert it gets called
        monkeypatch.setattr(mocksmtp, "sendmail", mock_sendmail)
        monkeypatch.setattr(smtplib, "SMTP_SSL", mocksmtp)

        self.mocksmtp = mocksmtp

    @pytest.mark.asyncio
    async def test_should_send_email_when_required_data_is_provided(self):
        """Should send an email when the required data is provided"""
        service = EmailService()
        await service.send(recipients=[self.recipient], subject=self.subject)
        self.mocksmtp.sendmail.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_throw_error_when_email_fails(self, monkeypatch):
        """
        Should throw an error when sending an email fails
        Ignore the monkeypatched smptlib and instead throw error
        by attempting to log in using incorrect credentials
        """
        monkeypatch.undo()
        service = EmailService()
        service.login_email_user = "mock_user"
        service.login_email_password = "mock_password"
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
