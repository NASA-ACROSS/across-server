import datetime
import importlib
from collections.abc import Generator
from types import ModuleType
from typing import Any, Iterable, Self
from unittest.mock import AsyncMock, MagicMock

import pytest
from argon2 import PasswordHasher
from fastapi import FastAPI

from across_server import core
from across_server.auth import strategies
from across_server.auth.schemas import SecretKeySchema
from across_server.db import models
from across_server.routes.v1.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.v1.user.service_account.service import ServiceAccountService


@pytest.fixture
def fake_service_account_data_with_secret(
    fake_service_account: dict,
    fake_generated_hex: str,
) -> core.schemas.ServiceAccountSecret:
    return core.schemas.ServiceAccountSecret.model_validate(
        {**fake_service_account.__dict__, "secret_key": fake_generated_hex}
    )


@pytest.fixture(scope="function")
def mock_service_account_service(
    fake_service_account: dict,
    fake_service_account_data_with_secret: core.schemas.ServiceAccountSecret,
) -> Generator[AsyncMock]:
    mock = AsyncMock(ServiceAccountService)

    mock.create = AsyncMock(return_value=fake_service_account_data_with_secret)
    mock.get = AsyncMock(return_value=fake_service_account)
    mock.get_many = AsyncMock(return_value=[fake_service_account])
    mock.update = AsyncMock(return_value=fake_service_account)
    mock.rotate_key = AsyncMock(return_value=fake_service_account_data_with_secret)
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


@pytest.fixture()
def fake_generated_hex() -> Iterable[str]:
    return "somegeneratedhex"


@pytest.fixture(autouse=True)
def mock_secrets(
    svc_mod: ModuleType, fake_generated_hex: str, monkeypatch: pytest.MonkeyPatch
) -> MagicMock:
    mock_secrets = MagicMock()
    mock_secrets.token_hex = MagicMock(return_value=fake_generated_hex)

    monkeypatch.setattr(svc_mod, "secrets", mock_secrets)

    return mock_secrets


@pytest.fixture()
def fake_secret_key_schema(
    fake_generated_hex: str, fixed_expiration: datetime.datetime
) -> SecretKeySchema:
    return SecretKeySchema(key=fake_generated_hex, expiration=fixed_expiration)


@pytest.fixture
def mock_password_hasher() -> MagicMock:
    mock = MagicMock()
    mock.hash = MagicMock(side_effect=lambda key: f"hash+{key}")

    return mock


@pytest.fixture(autouse=True)
def mock_refresh_sa(
    mock_refresh: AsyncMock, fake_service_account: models.ServiceAccount
) -> None:
    async def fake_refresh(instance: models.ServiceAccount) -> None:
        instance.id = fake_service_account.id

    mock_refresh.side_effect = fake_refresh


@pytest.fixture(autouse=True)
def svc_mod() -> ModuleType:
    svc = importlib.import_module(
        "across_server.routes.v1.user.service_account.service"
    )

    return svc


@pytest.fixture(autouse=True)
def monkeypatch_password_hasher(
    svc_mod: ModuleType,
    mock_password_hasher: PasswordHasher,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(svc_mod, "password_hasher", mock_password_hasher)


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
def fake_service_account_create() -> ServiceAccountCreate:
    return ServiceAccountCreate(
        name="test service account",
        description="test service account description",
        expiration_duration=20,
    )
