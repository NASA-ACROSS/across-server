from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from across_server.auth import security, strategies
from across_server.auth.service import AuthService
from across_server.util.email.service import EmailService


@pytest.fixture
def mock_auth_service():
    mock = AsyncMock(AuthService)
    mock.get_authenticated_user = AsyncMock(return_value="mocked_user")

    yield mock


@pytest.fixture
def mock_email_service():
    mock = AsyncMock(EmailService)
    mock.send = AsyncMock(return_value=True)

    yield mock


@pytest.fixture
def mock_webserver_access():
    mock = MagicMock(strategies.webserver_access)

    yield mock


@pytest.fixture(autouse=True)
def mock_magic_link_generate():
    with patch("across_server.auth.magic_link.generate") as mock:
        mock.return_value = "http://test/auth/verify?token=mock_token"

        yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app,
    fastapi_dep,
    mock_auth_service,
    mock_webserver_access,
    mock_email_service,
):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            EmailService: lambda: mock_email_service,
            AuthService: lambda: mock_auth_service,
            security.extract_creds: lambda: "credentials boyo",
            strategies.webserver_access: lambda: mock_webserver_access,
        }
    ):
        yield overrider
