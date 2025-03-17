from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from across_server.db.models import Instrument
from across_server.routes.instrument.service import InstrumentService


@pytest.fixture(scope="function")
def mock_instrument_service(mock_instrument_data: Instrument) -> Generator[AsyncMock]:
    mock = AsyncMock(InstrumentService)

    mock.get = AsyncMock(return_value=mock_instrument_data)
    mock.get_many = AsyncMock(return_value=[mock_instrument_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: MagicMock, mock_instrument_service: AsyncMock
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            InstrumentService: lambda: mock_instrument_service,
        }
    ):
        yield overrider
