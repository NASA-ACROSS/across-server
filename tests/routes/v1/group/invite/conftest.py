import uuid

import pytest

from across_server.db import models


@pytest.fixture
def mock_group_invite_data(
    mock_user_data: models.User, mock_group_data: models.Group
) -> models.GroupInvite:
    return models.GroupInvite(
        **{
            "id": uuid.UUID("02aa89d2-1b77-4a34-9504-063236b58782"),
            "group_id": uuid.UUID("03aa89d2-1b77-4a34-9504-063236b58782"),
            "receiver_id": uuid.UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
            "sender_id": uuid.UUID("04aa89d2-1b77-4a34-9504-063236b58782"),
            "receiver_email": "sandy@treedome.space",
            "receiver": mock_user_data,
            "group": mock_group_data,
        }
    )


@pytest.fixture(scope="function")
def mock_user_data() -> models.User:
    return models.User(
        **{
            "username": "SandyTheSquirrel",
            "first_name": "Sandy",
            "last_name": "Cheeks",
            "email": "sandy@treedome.space",
            "id": uuid.UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
            "roles": [],
            "groups": [],
            "group_roles": [],
            "service_accounts": [],
            "received_invites": [],
        }
    )
