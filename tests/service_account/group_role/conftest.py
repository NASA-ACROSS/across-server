import datetime
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from across_server.db import models
from across_server.routes.user.service import UserService
from across_server.routes.user.service_account.group_role.service import (
    ServiceAccountGroupRoleService,
)

date_format = "%Y-%m-%d %H:%M:%S"


@pytest.fixture
def mock_service_account_data():
    return models.ServiceAccount(
        **{
            "id": str(uuid4()),
            "user_id": UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
            "name": "test service account",
            "description": "test service account description",
            "secret_key": "very secret key",
            "expiration": datetime.datetime.strptime(
                "2026-01-30 00:00:00", date_format
            ),
            "expiration_duration": "30",
            "group_roles": [],
        }
    )


@pytest.fixture(scope="function")
def mock_service_account_group_role_service(mock_service_account_data):
    mock = AsyncMock(ServiceAccountGroupRoleService)

    mock.assign = AsyncMock(return_value=mock_service_account_data)
    mock.remove = AsyncMock(return_value=mock_service_account_data)

    yield mock


@pytest.fixture
def mock_group_role_data():
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
        }
    )


@pytest.fixture(scope="function")
def mock_user_data(mock_group_role_data):
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
def mock_user_service(mock_user_data):
    mock = AsyncMock(UserService).return_value = mock_user_data

    yield mock


@pytest.fixture(scope="function")
def frozen_time():
    return datetime.datetime(1993, 3, 13, 15, 13, 00)


@pytest.fixture(scope="function")
def patch_datetime_now(monkeypatch, frozen_time):
    class FrozenDatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return frozen_time

    monkeypatch.setattr(datetime, "datetime", FrozenDatetime)


@pytest.fixture(scope="function")
def frozen_expiration(frozen_time):
    return frozen_time - datetime.timedelta(days=3)
