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
from across_server.db.models import Instrument, Observatory, Telescope
from across_server.util.email.service import EmailService


@pytest.fixture(scope="module")
def app() -> FastAPI:
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
    return MagicMock(return_value="default mocked scalar result")


@pytest.fixture
def mock_scalars() -> Generator[MagicMock]:
    mock_result = MagicMock()
    yield mock_result


@pytest.fixture
def mock_result(
    mock_scalar_one_or_none: MagicMock, mock_scalars: MagicMock
) -> Generator[AsyncMock]:
    mock_result = AsyncMock(return_value="default result")
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_scalar_one_or_none)
    mock_result.scalars = MagicMock(return_value=mock_scalars)

    yield mock_result


@pytest.fixture
def mock_scalar_result() -> Generator[AsyncMock]:
    mock_result = AsyncMock()
    mock_result.all = MagicMock()
    mock_result.one = MagicMock()
    mock_result.one_or_none = MagicMock()

    yield mock_result


@pytest.fixture
def mock_db(
    mock_result: AsyncMock, mock_scalar_result: AsyncMock
) -> Generator[AsyncMock]:
    mock = AsyncMock(AsyncSession)

    # Mock the Result object that `execute` returns
    mock.execute = AsyncMock(return_value=mock_result)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    mock.scalars = AsyncMock(return_value=mock_scalar_result)
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
