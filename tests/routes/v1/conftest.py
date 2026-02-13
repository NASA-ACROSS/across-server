import datetime
from uuid import uuid4

import pytest

from across_server.db import models


@pytest.fixture(scope="session")
def version() -> str:
    return "v1"


@pytest.fixture
def fake_time() -> datetime.datetime:
    # server is set to UTC by default, we do not need to set timezones
    return datetime.datetime(1992, 12, 23, 19, 15, 00)


@pytest.fixture
def fixed_expiration(fake_time: datetime.datetime) -> datetime.datetime:
    return fake_time + datetime.timedelta(days=30)


@pytest.fixture
def fake_group(
    fake_group_role: models.GroupRole, fake_user: models.User
) -> models.Group:
    group = models.Group(
        **{
            "id": str(uuid4()),
            "name": "test group",
            "roles": [fake_group_role],
            "users": [fake_user],
        }
    )

    fake_group_role.group = group
    fake_user.groups = [group]

    return group


@pytest.fixture
def fake_service_account(
    fake_group_role: models.GroupRole,
    fixed_expiration: datetime.datetime,
) -> models.ServiceAccount:
    return models.ServiceAccount(
        **{
            "id": str(uuid4()),
            "name": "test service account",
            "description": "test service account description",
            "expiration": fixed_expiration,
            "expiration_duration": 30,
            "hashed_key": "$argon2id$v=19$m=65536,t=3,p=4$VDXb907Omm4z5LVJi0Ow21ZKb4/sX7pLlYcoFLlQzkBAJI9DVrhj4qViprBpNbGo1IHGLkBZJf2Ebstgpmr6ZQ$wcj2P9nYETGGunkhokRvD4v3lW6+i5tLPiL5EwDscC5kEIQTXJAfmcJCwGo6RsVGkLTR/gf5ppR/XxrFTZm6mw",
            "group_roles": [fake_group_role],
        }
    )


@pytest.fixture(scope="function")
def fake_user(
    fake_group_role: models.GroupRole,
    fake_service_account: models.ServiceAccount,
) -> models.User:
    user = models.User(
        **{
            "username": "SandyTheSquirrel",
            "first_name": "Sandy",
            "last_name": "Cheeks",
            "email": "sandy@treedome.space",
            "id": "e2c834a4-232c-420a-985e-eb5bc59aba24",
            "roles": [],
            "group_roles": [fake_group_role],
            "service_accounts": [fake_service_account],
        }
    )

    fake_service_account.user = [user]

    return user


@pytest.fixture
def fake_group_role(fake_permissions: list[models.Permission]) -> models.GroupRole:
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
            "permissions": fake_permissions,
        }
    )


@pytest.fixture(scope="function")
def fake_permissions() -> list[models.Permission]:
    return [
        models.Permission(
            **{
                "id": "e5b0b8a2-2b4a-4058-b4c2-eceab6908d19",
                "name": "group:schedule:write",
            },
        )
    ]
