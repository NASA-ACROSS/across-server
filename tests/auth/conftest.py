from collections.abc import Callable, Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi import FastAPI

from across_server.auth import security, strategies
from across_server.auth.service import AuthService
from across_server.util.email.service import EmailService


@pytest.fixture
def mock_auth_service() -> Generator[AsyncMock]:
    mock = AsyncMock(AuthService)
    mock.get_authenticated_user = AsyncMock(return_value="mocked_user")

    yield mock


@pytest.fixture(autouse=True)
def mock_magic_link_generate() -> Generator[AsyncMock]:
    with patch("across_server.auth.magic_link.generate") as mock:
        mock.return_value = "http://test/auth/verify?token=mock_token"

        yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: Callable,
    mock_auth_service: AsyncMock,
    mock_webserver_access: AsyncMock,
    mock_email_service: AsyncMock,
) -> Generator:
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
