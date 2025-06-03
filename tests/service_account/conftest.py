import datetime
import itertools
from collections.abc import Generator
from typing import Any, Iterable, Self
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

from across_server.auth import strategies
from across_server.auth.config import Config
from across_server.routes.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.user.service_account.service import ServiceAccountService


@pytest.fixture
def mock_service_account_data() -> dict:
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "test service account",
        "description": "test service account description",
        "expiration": "2025-01-30 00:00:00",
        "expiration_duration": "30",
        "group_roles": [],
    }


@pytest.fixture
def mock_service_account_data_with_secret() -> tuple[dict, str]:
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "test service account",
        "description": "test service account description",
        "expiration": "2025-01-30 00:00:00",
        "expiration_duration": "30",
        "group_roles": [],
    }, "very secret key"


@pytest.fixture(scope="function")
def mock_service_account_service(
    mock_service_account_data: dict,
    mock_service_account_data_with_secret: tuple[dict, str],
) -> Generator[AsyncMock]:
    mock = AsyncMock(ServiceAccountService)

    mock.create = AsyncMock(return_value=mock_service_account_data_with_secret)
    mock.get = AsyncMock(return_value=mock_service_account_data)
    mock.get_many = AsyncMock(return_value=[mock_service_account_data])
    mock.update = AsyncMock(return_value=mock_service_account_data)
    mock.rotate_key = AsyncMock(return_value=mock_service_account_data_with_secret)
    mock.expire_key = AsyncMock(return_value={})

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_service_account_service: AsyncMock,
    mock_global_access: MagicMock,
    mock_self_access: MagicMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ServiceAccountService: lambda: mock_service_account_service,
            strategies.global_access: lambda: mock_global_access,
            strategies.self_access: lambda: mock_self_access,
        }
    ):
        yield overrider


@pytest.fixture
def fake_time() -> datetime.datetime:
    return datetime.datetime(1992, 12, 23, 19, 15, 00, tzinfo=datetime.UTC)


@pytest.fixture
def mock_secrets_token_hex() -> Iterable[str]:
    return ["1", "2"]


@pytest.fixture()
def patch_secrets_token_hex(mock_secrets_token_hex: Iterable[str]) -> Any:
    with mock.patch(
        "secrets.token_hex", side_effect=itertools.cycle(mock_secrets_token_hex)
    ):
        yield


@pytest.fixture
def fixed_expiration(fake_time: datetime.datetime) -> datetime.datetime:
    return fake_time + datetime.timedelta(days=30)


@pytest.fixture
def patch_datetime_now(monkeypatch: Any, fake_time: datetime.datetime) -> None:
    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls, tz: datetime.tzinfo | None = None) -> Self:
            dt = fake_time.replace(tzinfo=tz) if tz else fake_time
            return cls.fromtimestamp(dt.timestamp(), tz=dt.tzinfo)

    monkeypatch.setattr(datetime, "datetime", mydatetime)


@pytest.fixture
def patch_config_secret(monkeypatch: Any) -> None:
    def patch_config_secret_fn(self: Any) -> str:
        return "TEST_SECRET"

    monkeypatch.setattr(
        Config,
        "SERVICE_ACCOUNT_SECRET_KEY",
        property(patch_config_secret_fn),
        raising=False,
    )


@pytest.fixture
def service_account_create_example() -> ServiceAccountCreate:
    return ServiceAccountCreate(
        name="test service account",
        description="test service account description",
        expiration_duration=20,
    )
