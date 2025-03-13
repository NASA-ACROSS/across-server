from unittest.mock import AsyncMock

import pytest

from across_server.routes.instrument.service import InstrumentService


@pytest.fixture(scope="function")
def mock_instrument_service(mock_instrument_data):
    mock = AsyncMock(InstrumentService)

    mock.get = AsyncMock(return_value=mock_instrument_data)
    mock.get_many = AsyncMock(return_value=[mock_instrument_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(app, fastapi_dep, mock_instrument_service):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            InstrumentService: lambda: mock_instrument_service,
        }
    ):
        yield overrider
