from unittest.mock import AsyncMock

import aiosmtplib
import fastapi
import pytest
import pytest_asyncio

from across_server.util.email.service import EmailService


class TestEmailService:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, monkeypatch, mock_db_session):
        self.recipient = "mockemail"
        self.subject = "Mock"

        class mocksmtp(aiosmtplib.SMTP):
            async def login(*args, **kwargs):
                pass

            async def sendmail(*args, **kwargs):
                pass

        mock_sendmail = AsyncMock()  # Need to mock to assert it gets called
        monkeypatch.setattr(mocksmtp, "sendmail", mock_sendmail)
        monkeypatch.setattr(aiosmtplib, "SMTP", mocksmtp)

        self.mocksmtp = mocksmtp

        self.db = mock_db_session

    @pytest.mark.asyncio
    async def test_should_send_email_when_required_data_is_provided(self):
        """Should send an email when the required data is provided"""
        service = EmailService(self.db)
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
        service = EmailService(self.db)
        service.login_email_user = "mock_user"
        service.login_email_password = "mock_password"
        with pytest.raises(Exception):
            await service.send(recipients=[self.recipient], subject=self.subject)

    @pytest.mark.asyncio
    async def test_should_throw_error_when_missing_recipients(self):
        """Should throw an error when sending an email without recipients"""
        service = EmailService(self.db)
        with pytest.raises(Exception):
            await service.send(subject=self.subject)  # type: ignore

    @pytest.mark.asyncio
    async def test_should_throw_error_when_missing_subject(self):
        """Should throw an error when sending an email without subject"""
        service = EmailService(self.db)
        with pytest.raises(Exception):
            await service.send(recipients=[self.recipient])  # type: ignore

    @pytest.mark.asyncio
    async def test_should_return_user_from_email(
        self, mock_scalar_one_or_none, mock_result
    ):
        """Should return a user that is associated with an email"""
        mock_scalar_one_or_none.return_value = self.recipient
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        self.db.execute.return_value = mock_result

        service = EmailService(self.db)
        user = await service.get_user_from_email(self.recipient)
        assert user == self.recipient

    @pytest.mark.asyncio
    async def test_should_throw_404_error_when_email_not_found(
        self, mock_scalar_one_or_none, mock_result
    ):
        """Should throw a 404 when no user is associated with an email"""
        mock_scalar_one_or_none.return_value = None
        mock_result.scalar_one_or_none = mock_scalar_one_or_none
        self.db.execute.return_value = mock_result

        service = EmailService(self.db)
        with pytest.raises(fastapi.HTTPException):
            await service.get_user_from_email(self.recipient)
