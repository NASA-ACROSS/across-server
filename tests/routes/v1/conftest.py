import datetime
from uuid import uuid4

import pytest

from across_server.core.schemas.coordinate import Coordinate
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
def fake_group_role_base() -> models.Group:
    return models.Group(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "test group",
            "short_name": "test",
        }
    )


@pytest.fixture
def fake_group_role(
    fake_permissions: list[models.Permission], fake_group_role_base: models.Group
) -> models.GroupRole:
    return models.GroupRole(
        **{
            "id": "12aa89d2-1b77-4a34-9504-063236b58782",
            "name": "Schedule Operations",
            "permissions": fake_permissions,
            "group": fake_group_role_base,
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


@pytest.fixture()
def fake_observation_data() -> models.Observation:
    coordinate = Coordinate(
        ra=123.456,
        dec=-87.65,
    )
    return models.Observation(
        id=uuid4(),
        instrument_id=uuid4(),
        schedule_id=uuid4(),
        object_name="Test Object",
        pointing_position=coordinate.create_gis_point(),
        pointing_ra=123.456,
        pointing_dec=-87.65,
        object_position=coordinate.create_gis_point(),
        object_ra=123.456,
        object_dec=-87.65,
        exposure_time=3600,
        min_wavelength=2000,
        max_wavelength=4000,
        peak_wavelength=3000,
        filter_name="Test Filter",
        date_range_begin=datetime.datetime(2024, 12, 16, 11, 0),
        date_range_end=datetime.datetime(2024, 12, 17, 11, 0),
        external_observation_id="test-external-obsid",
        type="imaging",
        status="planned",
        created_on=datetime.datetime.now(),
    )
