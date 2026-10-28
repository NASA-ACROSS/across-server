from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from across_server.db.models import Instrument
from across_server.routes.v1.instrument.service import InstrumentService


@pytest.fixture(scope="function")
def mock_instrument_service(fake_instrument_model: Instrument) -> Generator[AsyncMock]:
    mock = AsyncMock(InstrumentService)

    mock.get = AsyncMock(return_value=fake_instrument_model)
    mock.get_many = AsyncMock(return_value=[fake_instrument_model])

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
