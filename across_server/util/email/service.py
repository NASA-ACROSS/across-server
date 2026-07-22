from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import make_msgid

import aioboto3
import structlog
from aiobotocore.config import AioConfig

from across_server.auth import schemas
from across_server.db import models

from ...core.config import config as core_config
from .config import email_config

logger: structlog.stdlib.BoundLogger = structlog.get_logger()

_SES_RETRY_CONFIG = AioConfig(retries={"max_attempts": 4, "mode": "adaptive"})


class EmailService:
    def __init__(self) -> None:
        self.sender_email_addr = email_config.ACROSS_EMAIL
        self.region = email_config.AWS_SES_REGION
        self.source_arn = email_config.SES_SOURCE_ARN
        self.configuration_set = email_config.SES_CONFIGURATION_SET

    def construct_login_email(self, user: schemas.AuthUser, login_link: str) -> str:
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

    def construct_group_invitation_email(
        self,
        sender: models.User,
        receiver: models.User,
        group: models.Group,
        login_link: str,
    ) -> str:
        return f"""\
            <html>
            <p>Dear {receiver.first_name} {receiver.last_name},</p>
            <p>You have been invited to join the ACROSS user group:</p>
            <p><b>{group.name}</b></p>
            <p>by {sender.first_name} {sender.last_name} <i>{sender.email}</i></p>
            <p>Please follow the link below to login to your account and view the invitation
                on your profile page.</p>

            <a href="{login_link}">Login to your NASA-ACROSS account</a>
            <p>
                If you think that this message has been sent in error, please reach out to the sender above or contact an ACROSS administrator.
            <p>
            <p>
                Best,
            </p>
            <p>
                NASA-ACROSS
            </p>
            </html>
        """

    def construct_verification_email(self, user: models.User, magic_link: str) -> str:
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

    def filter_recipients(self, recipients: list[str]) -> list[str]:
        allowed = email_config.RESTRICTED_TO_EMAIL_LIST
        if not allowed:
            return recipients

        allowed_set = {addr.lower() for addr in allowed}
        return [recipient for recipient in recipients if recipient.lower() in allowed_set]

    async def send(
        self,
        recipients: list[str],
        subject: str,
        content_body: str | None = None,
        content_html: str | None = None,
        attachments: list = [],
    ) -> None:
        recipients = self.filter_recipients(recipients)
        if not recipients:
            logger.warning(
                "No permitted recipients after applying RESTRICTED_TO_EMAIL_LIST; skipping send",
                subject=subject,
            )
            return

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

        # only send emails in non-local envs
        if not core_config.is_local():
            session = aioboto3.Session()
            async with session.client(
                "ses",
                region_name=self.region,
                config=_SES_RETRY_CONFIG,
            ) as ses:
                await ses.send_raw_email(
                    Source=self.sender_email_addr,
                    Destinations=recipients,
                    RawMessage={"Data": em.as_string()},
                    SourceArn=self.source_arn,
                    ConfigurationSetName=self.configuration_set,
                )
