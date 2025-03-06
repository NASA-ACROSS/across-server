from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.db.models import Instrument as InstrumentModel
from across_server.routes.instrument.service import InstrumentService


@pytest.fixture()
def mock_instrument_data():
    return InstrumentModel(
        id=uuid4(), name="Test Instrument", short_name="TI", created_on=datetime.now()
    )


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
