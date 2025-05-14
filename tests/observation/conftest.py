from collections.abc import Callable, Generator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

from across_server.core.schemas.coordinate import Coordinate
from across_server.db.models import Observation
from across_server.routes.observation.service import ObservationService


@pytest.fixture()
def mock_observation_data() -> Observation:
    coordinate = Coordinate(
        ra=123.456,
        dec=-87.65,
    )
    return Observation(
        id=uuid4(),
        instrument_id=uuid4(),
        schedule_id=uuid4(),
        object_name="Test Object",
        pointing_position=coordinate.create_gis_point(),
        pointing_ra=123.456,
        pointing_dec=-87.65,
        object_position=coordinate.create_gis_point(),
        object_ra=123.456,
        object_dec=-87.65,
        exposure_time=3600,
        min_wavelength=2000,
        max_wavelength=4000,
        peak_wavelength=3000,
        filter_name="Test Filter",
        date_range_begin=datetime(2024, 12, 16, 11, 0),
        date_range_end=datetime(2024, 12, 17, 11, 0),
        external_observation_id="test-external-obsid",
        type="imaging",
        status="planned",
        created_on=datetime.now(),
    )


@pytest.fixture(scope="function")
def mock_telescope_service(mock_observation_data: None) -> Generator[AsyncMock]:
    mock = AsyncMock(ObservationService)

    mock.get = AsyncMock(return_value=mock_observation_data)
    mock.get_many = AsyncMock(return_value=[mock_observation_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: Callable, mock_telescope_service: AsyncMock
) -> Generator:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ObservationService: lambda: mock_telescope_service,
        }
    ):
        yield overrider


@pytest.fixture(
    params=[
        {"cone_search_ra": 123.456, "cone_search_dec": -87.65},
        {"cone_search_radius": 0.5},
        {"bandpass_min": 2000},
        {"depth_value": 20},
    ]
)
def bad_observation_filter(request: pytest.FixtureRequest) -> Any:
    """
    Parameters pop in the get_many routine to trigger 422
    """
    return request.param
