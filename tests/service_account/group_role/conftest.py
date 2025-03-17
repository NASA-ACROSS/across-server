from collections.abc import Generator
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from across_server.db import models
from across_server.routes.user.service import UserService
from across_server.routes.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)


@pytest.fixture
def mock_service_account_data() -> models.ServiceAccount:
    return models.ServiceAccount(
        **{
            "id": str(uuid4()),
            "user_id": UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
            "name": "test service account",
            "description": "test service account description",
            "secret_key": "very secret key",
            "expiration": "2025-03-13 00:00:00",
            "expiration_duration": "30",
            "group_roles": [],
        }
    )


@pytest.fixture(scope="function")
def mock_service_account_group_role_service(
    mock_service_account_data: models.ServiceAccount,
) -> Generator[AsyncMock]:
    mock = AsyncMock(ServiceAccountGroupRoleService)

    mock.assign = AsyncMock(return_value=mock_service_account_data)
    mock.remove = AsyncMock(return_value=mock_service_account_data)

    yield mock


@pytest.fixture
def mock_group_role_data() -> models.GroupRole:
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
        }
    )


@pytest.fixture(scope="function")
def mock_user_data(mock_group_role_data: models.GroupRole) -> models.User:
    return models.User(
        **{
            "username": "SandyTheSquirrel",
            "first_name": "Sandy",
            "last_name": "Cheeks",
            "email": "sandy@treedome.space",
            "id": "e2c834a4-232c-420a-985e-eb5bc59aba24",
            "roles": [],
            "group_roles": [mock_group_role_data],
        }
    )


@pytest.fixture(scope="function")
def mock_user_service(mock_user_data: models.User) -> Generator[models.User]:
    mock = AsyncMock(UserService).return_value = mock_user_data

    yield mock
