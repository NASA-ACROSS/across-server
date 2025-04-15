import pytest

from across_server.db import models


@pytest.fixture
def mock_group_invite_data() -> models.GroupInvite:
    return models.GroupInvite(
        **{
            "id": "02aa89d2-1b77-4a34-9504-063236b58782",
            "group_id": "03aa89d2-1b77-4a34-9504-063236b58782",
            "receiver_id": "04aa89d2-1b77-4a34-9504-063236b58782",
            "sender_id": "05aa89d2-1b77-4a34-9504-063236b58782",
            "receiver_email": "test_email@test.com",
        }
    )
