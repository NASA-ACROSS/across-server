from collections.abc import Callable, Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI

from across_server.auth import security, strategies
from across_server.auth.config import Config
from across_server.auth.service import AuthService
from across_server.db import models
from across_server.util.email.service import EmailService


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
            security.get_bearer_credentials: lambda: "credentials boyo",
            strategies.webserver_access: lambda: mock_webserver_access,
        }
    ):
        yield overrider


@pytest.fixture
def mock_hashlib_sha512_client() -> Generator[MagicMock]:
    with patch("hashlib.sha512") as mock_hashlib_sha512:
        yield mock_hashlib_sha512


@pytest.fixture
def patch_config_secret(monkeypatch: Any) -> None:
    def patch_config_secret_fn(self: Any) -> str:
        return "TEST_SECRET"

    monkeypatch.setattr(
        Config,
        "SERVICE_ACCOUNT_SECRET_KEY",
        property(patch_config_secret_fn),
        raising=False,
    )


@pytest.fixture(scope="function")
def mock_user_data(mock_group_role_data: models.GroupRole) -> models.User:
    return models.User(
        **{
            "id": str(uuid4()),
            "username": "mock_user",
            "first_name": "Mock",
            "last_name": "User",
            "email": "sandy@treedome.space",
            "groups": [],
            "roles": [],
            "group_roles": [mock_group_role_data],
            "received_invites": [],
        }
    )


@pytest.fixture
def mock_group_data() -> models.Group:
    return models.Group(
        **{
            "id": str(uuid4()),
            "name": "test group",
        }
    )


@pytest.fixture
def mock_group_role_data(
    mock_group_data: models.Group, mock_permissions_data: list[models.Permission]
) -> models.GroupRole:
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
            "group": mock_group_data,
            "permissions": mock_permissions_data,
        }
    )


@pytest.fixture
def mock_service_account_data(
    mock_group_role_data: models.GroupRole,
    mock_user_data: models.User,
) -> models.ServiceAccount:
    return models.ServiceAccount(
        **{
            "id": str(uuid4()),
            "user_id": UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
            "name": "test service account",
            "description": "test service account description",
            "expiration": "2025-03-13 00:00:00",
            "expiration_duration": "30",
            "group_roles": [mock_group_role_data],
            "user": mock_user_data,
        }
    )


@pytest.fixture(scope="function")
def mock_permissions_data() -> list[models.Permission]:
    return [
        models.Permission(
            **{
                "id": "e5b0b8a2-2b4a-4058-b4c2-eceab6908d19",
                "name": "group:schedule:write",
            },
        )
    ]
