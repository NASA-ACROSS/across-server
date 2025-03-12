import datetime
from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from across_server.auth import strategies
from across_server.db import models
from across_server.routes.tle import schemas
from across_server.routes.tle.service import TLEService


@pytest.fixture(scope="function")
def todays_epoch() -> datetime.datetime:
    return datetime.datetime.now()


@pytest.fixture(scope="function")
def todays_epoch_yyddd(todays_epoch: datetime.datetime) -> str:
    date_str = todays_epoch.strftime(
        "%y%j"
    )  # %y = last two digits of the year, %j = day of the year

    # Calculate fractional day
    fractional_day = (
        todays_epoch.hour / 24
        + todays_epoch.minute / 1440
        + todays_epoch.second / 86400
        + todays_epoch.microsecond / 86400000000
    )

    # Combine to get final format
    formatted_date = str(date_str) + f"{fractional_day:.8f}".lstrip("0")

    return formatted_date


@pytest.fixture(scope="function")
def mock_tle_data(todays_epoch_yyddd: str) -> dict:
    return {
        "norad_id": 12345,
        "satellite_name": "SWIFT",
        "tle1": f"1 28485U 04047A   {todays_epoch_yyddd}  .00027471  00000+0  86373-3 0  9997",
        "tle2": "2 28485  20.5557 285.8116 0006385  93.6070 266.5099 15.31053389110064",
        "epoch": str(datetime.datetime(2025, 2, 7, 0, 45, 29, 477088)),
    }


@pytest.fixture(scope="function")
def mock_tle_data_explorer_6() -> dict:
    return {
        "norad_id": 15,
        "satellite_name": "EXPLORER 6",
        "tle1": "1 00015U 59004A   59011.07596599  .00141866 +00000-0 +00000-0 0 09660",
        "tle2": "2 00015 047.0999 025.2139 7504899 076.7382 327.1285 02.03707726003008",
    }


@pytest.fixture(scope="function")
def mock_tle_data_invalid_epoch() -> dict:
    return {
        "norad_id": 25544,
        "satellite_name": "ISS",
        "tle1": "1 25544U 98067A   23500.69874537  .00016721  00000-0  30899-3 0  9993",
        "tle2": "2 25544  51.6415 329.4893 0003918  59.1794 300.9095 15.49591777399826",
    }


@pytest.fixture(scope="function")
def mock_tle(mock_tle_data: dict) -> schemas.TLECreate:
    return schemas.TLECreate(**mock_tle_data)


@pytest.fixture(scope="function")
def mock_tle_db(mock_tle_data: dict) -> models.TLE:
    return models.TLE(**mock_tle_data)


@pytest.fixture(scope="function")
def mock_tle_service(mock_tle_db: models.TLE) -> Generator[AsyncMock]:
    mock = AsyncMock(TLEService)

    mock.get = AsyncMock(return_value=mock_tle_db)
    mock.create = AsyncMock(return_value=mock_tle_db)
    mock.exists = AsyncMock(return_value=False)
    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_tle_service: MagicMock,
    mock_global_access: MagicMock,
) -> Generator:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            TLEService: lambda: mock_tle_service,
            strategies.global_access: lambda: mock_global_access,
        }
    ):
        yield overrider
