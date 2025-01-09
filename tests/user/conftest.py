from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

import across_server.auth as auth
from across_server.auth.service import AuthService
from across_server.routes.user.service import UserService


@pytest.fixture
def mock_user_data():
    return {
        "id": str(uuid4()),
        "username": "mock_user",
        "first_name": "Mock",
        "last_name": "User",
        "email": "mockuser@nasa.gov",
        "groups": [],
        "roles": [],
    }


@pytest.fixture(scope="function")
def mock_user_service(mock_user_data):
    mock = AsyncMock(UserService)

    mock.update = AsyncMock(return_value=mock_user_data)
    yield mock


@pytest.fixture(scope="function")
def mock_auth_service():
    mock = AsyncMock(AuthService)
    mock.authenticate = AsyncMock()
    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(app, fastapi_dep, mock_user_service, mock_auth_service):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            UserService: lambda: mock_user_service,
            auth.strategies.self_access: lambda: mock_auth_service,
        }
    ):
        yield overrider
