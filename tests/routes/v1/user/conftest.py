from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest
from fastapi import FastAPI

import across_server.auth as auth
from across_server.auth.service import AuthService
from across_server.db import models
from across_server.routes.v1.user.service import UserService
from across_server.util.email.service import EmailService


@pytest.fixture(scope="function")
def mock_user_json() -> dict:
    return {
        "username": "mock_user",
        "first_name": "Mock",
        "last_name": "User",
        "email": "sandy@treedome.space",
    }


@pytest.fixture(scope="function")
def mock_user_data() -> models.User:
    return models.User(
        **{
            "id": str(uuid4()),
            "username": "mock_user",
            "first_name": "Mock",
            "last_name": "User",
            "email": "sandy@treedome.space",
            "groups": [],
            "roles": [],
            "group_roles": [],
            "received_invites": [],
        }
    )


@pytest.fixture(scope="function")
def mock_user_service(mock_user_data: models.User) -> Generator[AsyncMock]:
    mock = AsyncMock(UserService)

    mock.update = AsyncMock(return_value=mock_user_data)
    mock.create = AsyncMock(return_value=mock_user_data)
    yield mock


@pytest.fixture(scope="function")
def mock_auth_service() -> Generator[AsyncMock]:
    mock = AsyncMock(AuthService)
    mock.authenticate = AsyncMock()
    mock.generate_magic_link = Mock(return_value="login magic link")
    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_email_service: AsyncMock,
    mock_user_service: AsyncMock,
    mock_auth_service: AsyncMock,
    mock_webserver_access: AsyncMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            EmailService: lambda: mock_email_service,
            UserService: lambda: mock_user_service,
            AuthService: lambda: mock_auth_service,
            auth.strategies.self_access: lambda: mock_auth_service,
            auth.strategies.webserver_access: lambda: mock_webserver_access,
        }
    ):
        yield overrider
