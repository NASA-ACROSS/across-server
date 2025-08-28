import uuid

import pytest

from across_server.db import models


@pytest.fixture
def fake_group_invite(
    fake_user: models.User, fake_group: models.Group
) -> models.GroupInvite:
    return models.GroupInvite(
        **{
            "id": uuid.UUID("02aa89d2-1b77-4a34-9504-063236b58782"),
            "group_id": uuid.UUID("03aa89d2-1b77-4a34-9504-063236b58782"),
            "receiver_id": uuid.UUID("e2c834a4-232c-420a-985e-eb5bc59aba24"),
            "sender_id": uuid.UUID("04aa89d2-1b77-4a34-9504-063236b58782"),
            "receiver_email": "sandy@treedome.space",
            "receiver": fake_user,
            "group": fake_group,
        }
    )
