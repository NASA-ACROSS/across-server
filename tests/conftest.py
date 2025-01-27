from unittest.mock import AsyncMock, MagicMock, Mock

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from across_server import main
from across_server.auth import strategies
from across_server.util.email.service import EmailService


@pytest.fixture(scope="module")
def app():
    return main.app


@pytest_asyncio.fixture(scope="module", autouse=True)
async def async_client(app: FastAPI):
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
def mock_scalar_one_or_none():
    return MagicMock(return_value="default mocked scalar result")


@pytest.fixture
def mock_result(mock_scalar_one_or_none):
    mock_result = AsyncMock(return_value="default result")
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_scalar_one_or_none)

    yield mock_result


@pytest.fixture
def mock_db(mock_result):
    mock = AsyncMock(AsyncSession)

    # Mock the Result object that `execute` returns
    mock.execute = AsyncMock(return_value=mock_result)

    yield mock


@pytest.fixture(scope="function")
def mock_db_session():
    mock = AsyncMock(AsyncSession)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()

    yield mock


@pytest.fixture
def mock_email_service():
    mock = AsyncMock(EmailService)
    mock.send = AsyncMock(return_value=True)

    yield mock


@pytest.fixture
def mock_webserver_access():
    mock = MagicMock(strategies.webserver_access)

    yield mock
