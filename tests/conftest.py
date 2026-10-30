from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, PropertyMock, patch
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from across_server import main
from across_server.auth import strategies
from across_server.auth.schemas import AuthUser
from across_server.db.models import (
    Filter,
    Group,
    Instrument,
    Observatory,
    Telescope,
)
from across_server.util.email.config import email_config
from across_server.util.email.service import EmailService


@pytest.fixture(scope="session")
def version() -> str | None:
    return None


@pytest.fixture(scope="module")
def app(version: str) -> FastAPI:
    # add conditional as new API versions are added here
    if version == "v1":
        return main.v1.api

    # still needed for health check route tests
    return main.app


@pytest_asyncio.fixture(scope="module", autouse=True)
async def async_client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient]:
    host, port = "127.0.0.1", 9000

    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=app,
            client=(host, port),
        ),
        base_url="http://test",
    )

    async with client:
        yield client


@pytest.fixture
def mock_scalar_one_or_none() -> MagicMock:
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_one_or_none() -> MagicMock:
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_scalar_one() -> MagicMock:
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_unique(mock_scalar_one_or_none: MagicMock) -> MagicMock:
    mock = MagicMock()
    mock.scalar_one_or_none = mock_scalar_one_or_none
    return mock


@pytest.fixture
def mock_tuples() -> MagicMock:
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_result(
    mock_scalar_one_or_none: MagicMock,
    mock_one_or_none: MagicMock,
    mock_scalar_one: MagicMock,
    mock_scalars: MagicMock,
    mock_unique: MagicMock,
    mock_tuples: MagicMock,
) -> MagicMock:
    mock = MagicMock()
    mock.unique = MagicMock(return_value=mock_unique)
    mock.scalars = MagicMock(return_value=mock_scalars)
    mock.scalar_one = mock_scalar_one
    mock.scalar_one_or_none = mock_scalar_one_or_none
    mock.one_or_none = mock_one_or_none
    mock.tuples = mock_tuples

    return mock


@pytest.fixture
def mock_scalars() -> AsyncMock:
    mock = AsyncMock()
    mock.all = MagicMock()
    mock.one = MagicMock()
    mock.one_or_none = MagicMock()

    return mock


@pytest.fixture
def mock_refresh() -> AsyncMock:
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_db(
    mock_result: AsyncMock,
    mock_scalars: AsyncMock,
    mock_refresh: AsyncMock,
) -> AsyncMock:
    mock = AsyncMock(AsyncSession)

    # Mock the Result object that `execute` returns
    mock.execute = AsyncMock(return_value=mock_result)
    mock.scalars = AsyncMock(return_value=mock_scalars)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.refresh = mock_refresh
    mock.delete = AsyncMock()

    return mock


@pytest.fixture(autouse=True)
def mock_email_config(monkeypatch: pytest.MonkeyPatch) -> Generator[MagicMock]:
    """Prevent email_config's SSM-backed properties from making real AWS calls in tests."""
    mock = MagicMock()
    mock.ALLOWED_TOP_LEVEL_DOMAINS = ["gov", "edu", "space"]
    mock.RESTRICTED_TO_EMAIL_LIST = ["sandy@treedome.space"]

    monkeypatch.setattr(
        type(email_config),
        "ALLOWED_TOP_LEVEL_DOMAINS",
        property(lambda _: mock.ALLOWED_TOP_LEVEL_DOMAINS),
    )
    monkeypatch.setattr(
        type(email_config),
        "RESTRICTED_TO_EMAIL_LIST",
        property(lambda _: mock.RESTRICTED_TO_EMAIL_LIST),
    )

    yield mock


@pytest.fixture
def fake_auth_user_or_none(fake_auth_user: AuthUser) -> AuthUser:
    return fake_auth_user


@pytest.fixture
def mock_email_service() -> AsyncMock:
    mock = AsyncMock(EmailService)
    mock.send = AsyncMock(return_value=True)

    return mock


@pytest.fixture
def mock_webserver_access() -> MagicMock:
    mock = MagicMock(strategies.webserver_access)

    return mock


@pytest.fixture
def mock_global_access() -> MagicMock:
    mock = MagicMock(strategies.global_access)

    return mock


@pytest.fixture
def mock_self_access() -> MagicMock:
    mock = MagicMock(strategies.self_access)
    mock.id = 1

    return mock


@pytest.fixture()
def fake_observatory_data(fake_group: Group) -> Observatory:
    return Observatory(
        id=uuid4(),
        name="Test Observatory",
        short_name="TO",
        type="GROUND_BASED",
        created_on=datetime.now(),
        group=fake_group,
    )


@pytest.fixture()
def fake_telescope_data(fake_observatory_data: Observatory) -> Telescope:
    return Telescope(
        id=uuid4(),
        name="Test Telescope",
        short_name="TT",
        created_on=datetime.now(),
        observatory=fake_observatory_data,
    )


@pytest.fixture()
def fake_instrument_model(fake_telescope_data: Telescope) -> Instrument:
    return Instrument(
        id=uuid4(),
        name="Test Instrument",
        short_name="TI",
        created_on=datetime.now(),
        is_observation_request_enabled=True,
        telescope=fake_telescope_data,
    )


@pytest.fixture()
def fake_filter_data(fake_instrument_model: Instrument) -> Filter:
    return Filter(
        id=uuid4(),
        name="Test Filter",
        created_on=datetime.now(),
        min_wavelength=5000,
        max_wavelength=6000,
        instrument_id=fake_instrument_model.id,
        is_operational=True,
    )


@pytest.fixture(autouse=True, scope="function")
def mock_core_config_is_local() -> Generator[PropertyMock]:
    """`False` by default, override with `mock_core_config_is_local.return_value = True`"""
    with patch(
        "across_server.core.config.Config.IS_LOCAL", new_callable=PropertyMock
    ) as mock_is_local:
        mock_is_local.return_value = False
        yield mock_is_local
