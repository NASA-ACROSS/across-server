from uuid import UUID, uuid4

import pytest

from across_server.db import models


@pytest.fixture
def mock_group_data(mock_group_role_data: models.GroupRole) -> models.Group:
    return models.Group(
        **{
            "id": str(uuid4()),
            "name": "test group",
            "roles": [mock_group_role_data],
            "users": [],  # gets populated with mock_user_data at runtime by the model because of groups relationship in mock_user_data below
        }
    )


@pytest.fixture
def mock_group_role_data(
    mock_permissions_data: list[models.Permission],
) -> models.GroupRole:
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
            "permissions": mock_permissions_data,
        }
    )


@pytest.fixture(scope="function")
def mock_user_data(
    mock_group_data: models.Group,
    mock_group_role_data: models.GroupRole,
    mock_service_account_data: models.ServiceAccount,
) -> models.User:
    return models.User(
        **{
            "username": "SandyTheSquirrel",
            "first_name": "Sandy",
            "last_name": "Cheeks",
            "email": "sandy@treedome.space",
            "id": "e2c834a4-232c-420a-985e-eb5bc59aba24",
            "roles": [],
            "groups": [mock_group_data],
            "group_roles": [mock_group_role_data],
            "service_accounts": [mock_service_account_data],
            "received_invites": [],
        }
    )


@pytest.fixture
def mock_service_account_data(
    mock_group_role_data: models.GroupRole,
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
