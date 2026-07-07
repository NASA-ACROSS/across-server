from collections.abc import Callable, Generator, Sequence
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest
from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums
from fastapi import FastAPI
from geoalchemy2 import WKTElement

from across_server.core.enums.depth_unit import DepthUnit
from across_server.core.enums.observation_status import ObservationStatus
from across_server.core.enums.observation_type import ObservationType
from across_server.core.schemas.coordinate import Coordinate
from across_server.core.schemas.date_range import DateRange
from across_server.db.models import Observation, ObservationFootprint
from across_server.routes.v1.observation.schemas import ObservationCreate
from across_server.routes.v1.observation.service import ObservationService


@pytest.fixture()
def fake_observation_footprint() -> ObservationFootprint:
    """Fixture that creates a mock ObservationFootprint"""
    return ObservationFootprint(
        id=uuid4(),
        observation_id=uuid4(),  # Will be overridden when attached to observation
        polygon=WKTElement(
            "POLYGON((123.0 -88.0, 124.0 -88.0, 124.0 -87.0, 123.0 -87.0, 123.0 -88.0))",
            srid=4326,
        ),
    )


@pytest.fixture()
def fake_observation_data_with_footprint(
    fake_observation_footprint: ObservationFootprint,
    fake_observation_data: Observation,
) -> Observation:
    # Add footprint to observation
    fake_observation_footprint.observation_id = fake_observation_data.id
    fake_observation_data.footprints = [fake_observation_footprint]

    return fake_observation_data


@pytest.fixture()
def fake_observation_pair(
    fake_observation_data: Observation,
) -> tuple[Observation, Observation, set[UUID]]:
    instrument_id_B = uuid4()

    obs_B = Observation(
        id=uuid4(),
        instrument_id=instrument_id_B,
        schedule_id=fake_observation_data.schedule_id,
        object_name=fake_observation_data.object_name,
        pointing_position=fake_observation_data.pointing_position,
        pointing_ra=fake_observation_data.pointing_ra,
        pointing_dec=fake_observation_data.pointing_dec,
        object_position=fake_observation_data.object_position,
        object_ra=fake_observation_data.object_ra,
        object_dec=fake_observation_data.object_dec,
        exposure_time=fake_observation_data.exposure_time,
        min_wavelength=fake_observation_data.min_wavelength,
        max_wavelength=fake_observation_data.max_wavelength,
        peak_wavelength=fake_observation_data.peak_wavelength,
        filter_name=fake_observation_data.filter_name,
        date_range_begin=fake_observation_data.date_range_begin,
        date_range_end=fake_observation_data.date_range_end,
        external_observation_id=fake_observation_data.external_observation_id,
        type=fake_observation_data.type,
        status=fake_observation_data.status,
        created_on=fake_observation_data.created_on,
    )

    return (
        fake_observation_data,
        obs_B,
        {fake_observation_data.instrument_id, instrument_id_B},
    )


@pytest.fixture()
def fake_observation_many(
    fake_observation_data_with_footprint: Observation,
) -> tuple[Sequence[Observation], int]:
    return ([fake_observation_data_with_footprint], 1)


@pytest.fixture()
def fake_observation_contains_point_many(
    fake_observation_data_with_footprint: Observation,
) -> tuple[Sequence[Observation], int]:
    return ([fake_observation_data_with_footprint], 1)


@pytest.fixture
def mock_observation_create() -> ObservationCreate:
    return ObservationCreate(
        instrument_id=uuid4(),
        object_name="test object",
        pointing_position=Coordinate(ra=123.456, dec=-87.65),
        date_range=DateRange(
            begin=datetime(2024, 12, 16, 11, 0),
            end=datetime(2024, 12, 17, 11, 0),
        ),
        external_observation_id="test-external-obsid",
        type=ObservationType.IMAGING,
        status=ObservationStatus.PLANNED,
        bandpass=WavelengthBandpass(
            min=2000, max=4000, unit=tools_enums.WavelengthUnit.ANGSTROM
        ),
    )


@pytest.fixture(scope="function")
def mock_observation_service(
    fake_observation_data_with_footprint: None,
    fake_observation_many: None,
    fake_observation_contains_point_many: None,
) -> Generator[AsyncMock]:
    mock = AsyncMock(ObservationService)

    mock.get = AsyncMock(return_value=fake_observation_data_with_footprint)
    mock.get_many = AsyncMock(return_value=fake_observation_many)
    mock.get_contains_point = AsyncMock(
        return_value=fake_observation_contains_point_many
    )

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: Callable, mock_observation_service: AsyncMock
) -> Generator:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ObservationService: lambda: mock_observation_service,
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


@pytest.fixture(
    params=[
        {"bandpass_min": 2000},
        {"bandpass_max": 4000},
        {"bandpass_type": tools_enums.WavelengthUnit.ANGSTROM},
        {"depth_value": 20},
        {"depth_unit": DepthUnit.AB_MAG},
    ]
)
def bad_point_overlap_filter(request: pytest.FixtureRequest) -> Any:
    """Parameters used in get_overlap_point to trigger InvalidObservationReadParametersException."""
    return request.param
