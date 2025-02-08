import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from across_server.auth import strategies
from across_server.db import models
from across_server.routes.tle import schemas
from across_server.routes.tle.service import TLEService


@pytest.fixture(scope="function")
def mock_tle_data():
    return {
        "norad_id": 12345,
        "satellite_name": "SWIFT",
        "tle1": "1 28485U 04047A   25038.03159117  .00027471  00000+0  86373-3 0  9997",
        "tle2": "2 28485  20.5557 285.8116 0006385  93.6070 266.5099 15.31053389110064",
        "epoch": str(datetime.datetime(2025, 2, 7, 0, 45, 29, 477088)),
    }


@pytest.fixture(scope="function")
def mock_tle(mock_tle_data):
    return schemas.TLECreate(**mock_tle_data)


@pytest.fixture(scope="function")
def mock_tle_db(mock_tle_data):
    return models.TLE(**mock_tle_data)


@pytest.fixture
def mock_global_access():
    mock = MagicMock(strategies.global_access)

    yield mock


@pytest.fixture(scope="function")
def mock_tle_service(mock_tle_db):
    mock = AsyncMock(TLEService)

    mock.get = AsyncMock(return_value=mock_tle_db)
    mock.create = AsyncMock(return_value=mock_tle_db)
    mock.exists = AsyncMock(return_value=False)
    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(app, fastapi_dep, mock_tle_service, mock_global_access):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            TLEService: lambda: mock_tle_service,
            strategies.global_access: lambda: mock_global_access,
        }
    ):
        yield overrider
