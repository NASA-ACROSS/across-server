from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest

from across_server.db import models
from across_server.routes.v1.user.service import UserService
from across_server.routes.v1.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)


@pytest.fixture(scope="function")
def mock_service_account_group_role_service(
    fake_service_account: models.ServiceAccount,
) -> Generator[AsyncMock]:
    mock = AsyncMock(ServiceAccountGroupRoleService)

    mock.assign = AsyncMock(return_value=fake_service_account)
    mock.remove = AsyncMock(return_value=fake_service_account)

    yield mock


@pytest.fixture
def fake_group_role_data() -> models.GroupRole:
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
        }
    )


@pytest.fixture(scope="function")
def mock_user_service(fake_user: models.User) -> Generator[models.User]:
    mock = AsyncMock(UserService).return_value = fake_user

    yield mock
