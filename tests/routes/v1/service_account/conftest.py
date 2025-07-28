import datetime
import importlib
import itertools
from collections.abc import Generator
from typing import Any, Iterable, Self
from unittest import mock
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

from across_server.auth import strategies
from across_server.auth.schemas import SecretKeySchema
from across_server.db import models
from across_server.routes.v1.user.service_account import schemas
from across_server.routes.v1.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.v1.user.service_account.service import ServiceAccountService


@pytest.fixture
def mock_service_account_data() -> dict:
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "test service account",
        "description": "test service account description",
        "expiration": "2025-01-30 00:00:00",
        "expiration_duration": 30,
        "group_roles": [],
    }


@pytest.fixture
def mock_service_account_record(mock_service_account_data) -> models.ServiceAccount:
    return models.ServiceAccount(**mock_service_account_data)


@pytest.fixture()
def mock_secret_key() -> str:
    return "very secret key"


@pytest.fixture
def mock_service_account_data_with_secret(
    mock_service_account_data,
    mock_secret_key,
) -> schemas.ServiceAccountSecret:
    return schemas.ServiceAccountSecret.model_validate(
        {**mock_service_account_data, "secret_key": mock_secret_key}
    )


@pytest.fixture(scope="function")
def mock_service_account_service(
    mock_service_account_data: dict,
    mock_service_account_data_with_secret: schemas.ServiceAccountSecret,
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


@pytest.fixture(autouse=True)
def patch_secrets_token_hex(mock_secrets_token_hex: Iterable[str]) -> Any:
    with mock.patch(
        "secrets.token_hex", side_effect=itertools.cycle(mock_secrets_token_hex)
    ):
        yield


@pytest.fixture()
def mock_secret_key_schema(mock_secret_key, fixed_expiration):
    return SecretKeySchema(key=mock_secret_key, expiration=fixed_expiration)


@pytest.fixture()
def mock_generate_secret_key(mock_secret_key_schema: SecretKeySchema) -> MagicMock:
    mock = MagicMock(return_value=mock_secret_key_schema)

    return mock


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    mock = MagicMock()
    mock.hash = MagicMock(side_effect=lambda key: f"hash+{key}")

    return mock


@pytest.fixture(autouse=True)
def mock_refresh_sa(
    mock_refresh: AsyncMock, mock_service_account_record: models.ServiceAccount
) -> None:
    async def fake_refresh(instance: models.ServiceAccount) -> None:
        instance.id = mock_service_account_record.id

    mock_refresh.side_effect = fake_refresh


@pytest.fixture(autouse=True)
def svc_mod() -> Any:
    svc = importlib.import_module(
        "across_server.routes.v1.user.service_account.service"
    )

    return svc


@pytest.fixture(autouse=True)
def patch_password_hasher(svc_mod, mock_password_hasher, monkeypatch) -> Any:
    monkeypatch.setattr(svc_mod, "password_hasher", mock_password_hasher)


@pytest.fixture(autouse=True)
def monkeypatch_generate_secret_key(
    monkeypatch: pytest.MonkeyPatch, mock_generate_secret_key, svc_mod
) -> Any:
    """
    Monkey‑patch the exact symbol that your ServiceAccountService.create()
    calls: the name `generate_secret_key` in the service module’s globals.
    """

    monkeypatch.setattr(svc_mod, "generate_secret_key", mock_generate_secret_key)


@pytest.fixture
def fixed_expiration(fake_time: datetime.datetime) -> datetime.datetime:
    return fake_time + datetime.timedelta(days=30)


@pytest.fixture(autouse=True)
def patch_datetime_now(monkeypatch: Any, fake_time: datetime.datetime) -> None:
    class MockDatetime(datetime.datetime):
        @classmethod
        def now(cls, tz: datetime.tzinfo | None = None) -> Self:
            dt = fake_time.replace(tzinfo=tz) if tz else fake_time
            return cls.fromtimestamp(dt.timestamp(), tz=dt.tzinfo)

    monkeypatch.setattr(datetime, "datetime", MockDatetime)


@pytest.fixture
def service_account_create_example() -> ServiceAccountCreate:
    return ServiceAccountCreate(
        name="test service account",
        description="test service account description",
        expiration_duration=20,
    )
