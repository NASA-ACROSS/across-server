import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid
from typing import List, Optional

from across_server.auth import schemas

from ...db import models
from .config import email_config


class EmailService:
    def __init__(self) -> None:
        self.sender_email_addr = email_config.ACROSS_EMAIL
        self.login_email_user = email_config.ACROSS_EMAIL_USER
        self.login_email_password = email_config.ACROSS_EMAIL_PASSWORD
        self.smtp_host = email_config.ACROSS_EMAIL_HOST
        self.smtp_port = int(email_config.ACROSS_EMAIL_PORT)

    @staticmethod
    def construct_login_email(user: schemas.AuthUser, login_link: str):
        return f"""\
            <html>
            <p>Dear {user.first_name} {user.last_name},</p>
            <p>
                Please use the following link to login to your account.
                This link will expire in 15 minutes.
            </p>
            <a href="{login_link}">Login to your NASA-ACROSS account</a>
            <p>
                If you think that this has been done in error, please contact an ACROSS administrator:
            <p>
            <p>
                Best,
            </p>
            <p>
                NASA-ACROSS
            </p>
            </html>
        """

    @staticmethod
    def construct_verification_email(user: models.User, magic_link: str):
        return f"""\
            <html>
            <p>Dear {user.first_name} {user.last_name},</p>
            <p>
                An account with the username: {user.username} has been created with this email.
                Please use the following link to login and verify your account.
                After doing so, you will have access to your NASA ACROSS API <ttt>api_token</ttt>
                which can be used to access the API endpoints within the NASA-ACROSS framework.
                This link will expire in 15 minutes.
            </p>
            <a href="{magic_link}">Verify your account</a>
            <p>
                If you think that this has been done in error, please contact an ACROSS administrator:
            <p>
            <p>
                Best,
            </p>
            <p>
                NASA-ACROSS
            </p>
            </html>
        """

    async def send(
        self,
        recipients: List[str],
        subject: str,
        content_body: Optional[str] = None,
        content_html: Optional[str] = None,
        attachments=[],
    ) -> None:
        em = MIMEMultipart("alternative")
        em["From"] = self.sender_email_addr
        em["To"] = ",".join(recipients)
        em["Subject"] = subject
        em["Message-ID"] = make_msgid(
            idstring="ACROSS/API/Login", domain=self.sender_email_addr.split("@")[-1]
        )

        if content_body:
            em.attach(MIMEText(content_body, "plain"))
        if content_html:
            em.attach(MIMEText(content_html, "html"))
        if attachments:
            # TODO: configure attachments, not sure if we will need this yet
            pass

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(
            host=self.smtp_host, port=self.smtp_port, context=context
        ) as smtp:
            smtp.login(self.login_email_user, self.login_email_password)
            smtp.sendmail(self.sender_email_addr, recipients, em.as_string())
