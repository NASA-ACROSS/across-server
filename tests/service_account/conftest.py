import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.auth import security, strategies
from across_server.auth.config import Config
from across_server.auth.service import AuthService
from across_server.routes.user.service_account.schemas import ServiceAccountCreate
from across_server.routes.user.service_account.service import ServiceAccountService


@pytest.fixture
def mock_service_account_data():
    return {
        "id": str(uuid4()),
        "user_id": str(uuid4()),
        "name": "test service account",
        "description": "test service account description",
        "secret_key": "very secret key",
        "expiration": "2025-01-30 00:00:00",
        "expiration_duration": "30",
    }


@pytest.fixture(scope="function")
def mock_service_account_service(mock_service_account_data):
    mock = AsyncMock(ServiceAccountService)

    mock.create = AsyncMock(return_value=mock_service_account_data)
    mock.get = AsyncMock(return_value=mock_service_account_data)
    mock.get_many = AsyncMock(return_value=[mock_service_account_data])
    mock.update = AsyncMock(return_value=mock_service_account_data)
    mock.expire_key = AsyncMock(return_value={})

    yield mock


@pytest.fixture(scope="function")
def mock_db_session():
    mock = AsyncMock(AsyncSession)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()

    yield mock


@pytest.fixture
def mock_global_access():
    mock = MagicMock(strategies.global_access)

    yield mock


@pytest.fixture
def mock_auth_service():
    mock = AsyncMock(AuthService)
    mock.get_authenticated_user = AsyncMock(return_value="mocked_user")
    mock.auth_user = AsyncMock(return_value="mocked_user")

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app,
    fastapi_dep,
    mock_service_account_service,
    mock_auth_service,
    mock_global_access,
):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ServiceAccountService: lambda: mock_service_account_service,
            AuthService: lambda: mock_auth_service,
            security.extract_creds: lambda: "credentials boyo",
            strategies.global_access: lambda: mock_global_access,
        }
    ):
        yield overrider


@pytest.fixture
def fake_time():
    return datetime.datetime(1992, 12, 23, 19, 15, 00)


@pytest.fixture
def baked_secret():
    return "244a7c90531f348359ec08ab10242741d22e2be75fdc6a003f53c9d8ebe0f8751c844c0ff55dcb43567643ad2750c97d761e9cf3d8728fb3d706cc184276063f"


@pytest.fixture
def patch_datetime_now(monkeypatch, fake_time):
    class mydatetime(datetime.datetime):
        @classmethod
        def now(cls):
            return fake_time

    monkeypatch.setattr(datetime, "datetime", mydatetime)


@pytest.fixture
def patch_config_secret(monkeypatch):
    def patch_config_secret_fn(self):
        return "TEST_SECRET"

    monkeypatch.setattr(
        Config,
        "SERVICE_ACCOUNT_SECRET_KEY",
        property(patch_config_secret_fn),
        raising=False,
    )


@pytest.fixture()
def service_account_create_example():
    return ServiceAccountCreate(
        name="test service account",
        description="test service account description",
        expiration_duration=20,
    )
