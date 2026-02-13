import datetime
from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from across_server.auth import security, strategies
from across_server.auth.service import AuthService
from across_server.db import models
from across_server.util.email.service import EmailService


@pytest.fixture(autouse=True)
def set_fake_service_account_expiration(
    fake_service_account: models.ServiceAccount, fake_time: datetime.datetime
) -> None:
    fake_service_account.expiration = fake_time


@pytest.fixture(autouse=True)
def patch_datetime_now(monkeypatch: Any, fake_time: datetime.datetime) -> None:
    def real_datetime_class(*args: Any, **kwargs: Any) -> datetime.datetime:
        return datetime.datetime(*args, **kwargs)

    datetime_mock = MagicMock(wraps=datetime.datetime, side_effect=real_datetime_class)
    datetime_mock.now.return_value = fake_time

    monkeypatch.setattr(datetime, "datetime", datetime_mock)


@pytest.fixture
def mock_auth_service() -> Generator[AsyncMock]:
    mock = AsyncMock(AuthService)
    mock.get_authenticated_user = AsyncMock(return_value="mocked_user")
    mock.authenticate_user = AsyncMock(return_value="mocked_user")
    mock.authenticate_service_account = AsyncMock(return_value="mocked_user")
    yield mock


@pytest.fixture(autouse=True)
def mock_magic_link_generate() -> Generator[AsyncMock]:
    with patch("across_server.auth.magic_link.generate") as mock:
        mock.return_value = "http://frontend-test/user/login-verify?token=mock_token"

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
            security.get_bearer_credentials: lambda: "credentials boyo",
            strategies.webserver_access: lambda: mock_webserver_access,
        }
    ):
        yield overrider
