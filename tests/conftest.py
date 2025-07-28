from collections.abc import AsyncGenerator, Generator
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from across_server import main
from across_server.auth import strategies
from across_server.db.models import Filter, Instrument, Observatory, Telescope
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
def mock_scalar_one_or_none() -> Generator[MagicMock]:
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_scalars() -> Generator[MagicMock]:
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_unique(mock_scalar_one_or_none: MagicMock) -> Generator[MagicMock]:
    mock = MagicMock()
    mock.scalar_one_or_none = mock_scalar_one_or_none
    yield mock


@pytest.fixture
def mock_tuples() -> Generator[MagicMock]:
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_result(
    mock_scalar_one_or_none: MagicMock,
    mock_scalars: MagicMock,
    mock_unique: MagicMock,
    mock_tuples: MagicMock,
) -> Generator[MagicMock]:
    mock = MagicMock()
    mock.unique = MagicMock(return_value=mock_unique)
    mock.scalar_one_or_none = mock_scalar_one_or_none
    mock.scalars = mock_scalars
    mock.tuples = mock_tuples

    yield mock


@pytest.fixture
def mock_scalar_result() -> Generator[AsyncMock]:
    mock = AsyncMock()
    mock.all = MagicMock()
    mock.one = MagicMock()
    mock.one_or_none = MagicMock()

    yield mock


@pytest.fixture
def mock_refresh() -> AsyncMock:
    mock = AsyncMock()
    return mock


@pytest.fixture
def mock_db(
    mock_result: AsyncMock,
    mock_scalar_result: AsyncMock,
    mock_refresh: AsyncMock,
) -> Generator[AsyncMock]:
    mock = AsyncMock(AsyncSession)

    # Mock the Result object that `execute` returns
    mock.execute = AsyncMock(return_value=mock_result)
    mock.scalars = AsyncMock(return_value=mock_scalar_result)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.refresh = mock_refresh
    mock.delete = AsyncMock()

    yield mock


@pytest.fixture
def mock_email_service() -> Generator[AsyncMock]:
    mock = AsyncMock(EmailService)
    mock.send = AsyncMock(return_value=True)

    yield mock


@pytest.fixture
def mock_webserver_access() -> Generator[MagicMock]:
    mock = MagicMock(strategies.webserver_access)

    yield mock


@pytest.fixture
def mock_global_access() -> Generator[MagicMock]:
    mock = MagicMock(strategies.global_access)

    yield mock


@pytest.fixture
def mock_self_access() -> Generator[MagicMock]:
    mock = MagicMock(strategies.self_access)
    mock.id = 1

    yield mock


@pytest.fixture()
def mock_observatory_data() -> Observatory:
    return Observatory(
        id=uuid4(),
        name="Test Observatory",
        short_name="TO",
        type="GROUND_BASED",
        created_on=datetime.now(),
    )


@pytest.fixture()
def mock_telescope_data(mock_observatory_data: Observatory) -> Telescope:
    return Telescope(
        id=uuid4(),
        name="Test Telescope",
        short_name="TT",
        created_on=datetime.now(),
        observatory=mock_observatory_data,
    )


@pytest.fixture()
def mock_instrument_data(mock_telescope_data: Telescope) -> Instrument:
    return Instrument(
        id=uuid4(),
        name="Test Instrument",
        short_name="TI",
        created_on=datetime.now(),
        telescope=mock_telescope_data,
    )


@pytest.fixture()
def mock_filter_data(mock_instrument_data: Instrument) -> Filter:
    return Filter(
        id=uuid4(),
        name="Test Filter",
        created_on=datetime.now(),
        min_wavelength=5000,
        max_wavelength=6000,
        instrument_id=mock_instrument_data.id,
        is_operational=True,
    )
