from collections.abc import Generator
from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums
from fastapi import FastAPI

from across_server.core.enums import ScheduleFidelity, ScheduleStatus
from across_server.core.enums.instrument_fov import InstrumentFOV
from across_server.core.enums.observation_status import ObservationStatus
from across_server.core.enums.observation_type import ObservationType
from across_server.core.schemas import Coordinate, DateRange
from across_server.db.models import Instrument as InstrumentModel
from across_server.db.models import Observation as ObservationModel
from across_server.db.models import Schedule as ScheduleModel
from across_server.db.models import Telescope as TelescopeModel
from across_server.routes.v1.observation.schemas import ObservationCreate
from across_server.routes.v1.schedule import service
from across_server.routes.v1.schedule.schemas import ScheduleCreate, ScheduleCreateMany
from across_server.routes.v1.schedule.service import ScheduleService
from across_server.routes.v1.telescope.access import telescope_access
from across_server.routes.v1.telescope.service import TelescopeService


@pytest.fixture
def mock_schedule_post_data() -> dict:
    return {
        "telescope_id": str(uuid4()),
        "date_range": {
            "begin": str(datetime.now()),
            "end": str(datetime.now() + timedelta(days=1)),
        },
        "status": "planned",
        "name": "Test Schedule",
        "external_id": "test_schedule_external_id",
        "fidelity": "low",
        "observation_count": 1,
        "observations": [
            {
                "instrument_id": str(uuid4()),
                "object_name": "test observation",
                "pointing_position": {"ra": 42, "dec": 42},
                "date_range": {
                    "begin": str(datetime.now()),
                    "end": str(datetime.now() + timedelta(seconds=45)),
                },
                "external_observation_id": "external",
                "type": "imaging",
                "status": "planned",
                "pointing_angle": 0,
                "exposure_time": 45,
                "reason": "test reasons",
                "description": "testing",
                "object_position": {"ra": 42, "dec": 42},
                "depth": {"value": 21, "unit": "ab_mag"},
                "bandpass": {
                    "filter_name": "g",
                    "central_wavelength": 5500,
                    "bandwidth": 1000,
                    "unit": "angstrom",
                },
            }
        ],
    }


@pytest.fixture
def mock_schedule_post_many_data() -> dict:
    mock_telescope_id = str(uuid4())

    return {
        "schedules": [
            {
                "telescope_id": mock_telescope_id,
                "date_range": {
                    "begin": str(datetime.now()),
                    "end": str(datetime.now() + timedelta(days=1)),
                },
                "status": "planned",
                "name": "Test Schedule",
                "external_id": "test_schedule_external_id",
                "fidelity": "low",
                "observation_count": 1,
                "observations": [
                    {
                        "instrument_id": str(uuid4()),
                        "object_name": "test observation",
                        "pointing_position": {"ra": 42, "dec": 42},
                        "date_range": {
                            "begin": str(datetime.now()),
                            "end": str(datetime.now() + timedelta(seconds=45)),
                        },
                        "external_observation_id": "external",
                        "type": "imaging",
                        "status": "planned",
                        "pointing_angle": 0,
                        "exposure_time": 45,
                        "reason": "test reasons",
                        "description": "testing",
                        "object_position": {"ra": 42, "dec": 42},
                        "depth": {"value": 21, "unit": "ab_mag"},
                        "bandpass": {
                            "filter_name": "g",
                            "central_wavelength": 5500,
                            "bandwidth": 1000,
                            "unit": "angstrom",
                        },
                    }
                ],
            },
            {
                "telescope_id": mock_telescope_id,
                "date_range": {
                    "begin": str(datetime.now()),
                    "end": str(datetime.now() + timedelta(days=1)),
                },
                "status": "scheduled",
                "name": "Test Schedule 2",
                "external_id": "test_schedule_external_id_2",
                "fidelity": "low",
                "observation_count": 1,
                "observations": [
                    {
                        "instrument_id": str(uuid4()),
                        "object_name": "test observation",
                        "pointing_position": {"ra": 42, "dec": 42},
                        "date_range": {
                            "begin": str(datetime.now()),
                            "end": str(datetime.now() + timedelta(seconds=45)),
                        },
                        "external_observation_id": "external",
                        "type": "imaging",
                        "status": "planned",
                        "pointing_angle": 0,
                        "exposure_time": 45,
                        "reason": "test reasons",
                        "description": "testing",
                        "object_position": {"ra": 42, "dec": 42},
                        "depth": {"value": 21, "unit": "ab_mag"},
                        "bandpass": {
                            "filter_name": "g",
                            "central_wavelength": 5500,
                            "bandwidth": 1000,
                            "unit": "angstrom",
                        },
                    }
                ],
            },
        ],
        "telescope_id": mock_telescope_id,
    }


@pytest.fixture()
def fake_schedule_data(
    mock_schedule_post_data: dict, fake_observation_data: ObservationModel
) -> ScheduleModel:
    return ScheduleModel(
        id=uuid4(),
        telescope_id=UUID(mock_schedule_post_data["telescope_id"]),
        date_range_begin=datetime.now(),
        date_range_end=datetime.now() + timedelta(days=1),
        status=mock_schedule_post_data["status"],
        name=mock_schedule_post_data["name"],
        external_id=mock_schedule_post_data["external_id"],
        fidelity=mock_schedule_post_data["fidelity"],
        telescope=TelescopeModel(id=UUID(mock_schedule_post_data["telescope_id"])),
        observation_count=1,
        observations=[fake_observation_data],
        created_on=datetime.now(),
        created_by_id=uuid4(),
        checksum="checked sum",
    )


@pytest.fixture()
def fake_observation_data() -> ObservationModel:
    coordinate = Coordinate(
        ra=123.456,
        dec=-87.65,
    )
    return ObservationModel(
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


@pytest.fixture()
def mock_telescope_data(mock_schedule_post_data: dict) -> TelescopeModel:
    return TelescopeModel(
        id=UUID(mock_schedule_post_data["telescope_id"]),
        instruments=[
            InstrumentModel(
                id=UUID(mock_schedule_post_data["observations"][0]["instrument_id"]),
            )
        ],
    )


@pytest.fixture(scope="function")
def mock_schedule_service(fake_schedule_data: ScheduleModel) -> Generator[AsyncMock]:
    mock = AsyncMock(ScheduleService)

    mock.create = AsyncMock(return_value=uuid4())
    mock.get = AsyncMock(return_value=fake_schedule_data)
    mock.get_many = AsyncMock(return_value=[(fake_schedule_data, 1)])
    mock.get_history = AsyncMock(return_value=[(fake_schedule_data, 1)])
    mock.create_many = AsyncMock(return_value=[uuid4(), uuid4()])

    yield mock


@pytest.fixture(scope="function")
def mock_telescope_service(mock_telescope_data: TelescopeModel) -> Generator[AsyncMock]:
    mock = AsyncMock(TelescopeService)

    mock.get = AsyncMock(return_value=mock_telescope_data)

    yield mock


@pytest.fixture
def mock_telescope_access() -> Generator[MagicMock]:
    mock = MagicMock(telescope_access)
    mock.id = 1

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_schedule_service: AsyncMock,
    mock_telescope_service: AsyncMock,
    mock_telescope_access: MagicMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ScheduleService: lambda: mock_schedule_service,
            TelescopeService: lambda: mock_telescope_service,
            telescope_access: lambda: mock_telescope_access,
        }
    ):
        yield overrider


@pytest.fixture
def patch_service_get_from_checksum_none(monkeypatch: Any) -> None:
    class myschedule_service(ScheduleService):
        @classmethod
        def get_from_checksum(cls, checksum: str) -> None:
            return None

    monkeypatch.setattr(service, "ScheduleService", myschedule_service)


@pytest.fixture()
def schedule_create_example(mock_schedule_post_data: dict) -> ScheduleCreate:
    instrument_id = uuid4()

    observation_create = ObservationCreate(
        instrument_id=instrument_id,
        object_name="Test Object",
        pointing_position=Coordinate(
            ra=42,
            dec=42,
        ),
        date_range=DateRange(
            begin=datetime.now(), end=datetime.now() + timedelta(seconds=45)
        ),
        external_observation_id="external",
        type=ObservationType.IMAGING,
        status=ObservationStatus.PLANNED,
        pointing_angle=0,
        bandpass=WavelengthBandpass(
            filter_name="g",
            central_wavelength=5500,
            bandwidth=1000,
            unit=tools_enums.WavelengthUnit.ANGSTROM,
        ),
    )

    return ScheduleCreate(
        name="test service account",
        telescope_id=mock_schedule_post_data["telescope_id"],
        date_range=DateRange(
            begin=datetime.now(), end=datetime.now() + timedelta(days=1)
        ),
        status=ScheduleStatus.PLANNED,
        external_id="external_id",
        fidelity=ScheduleFidelity.LOW,
        observations=[observation_create],
    )


@pytest.fixture
def schedule_create_many_example(
    schedule_create_example: ScheduleCreate,
    mock_schedule_post_data: dict,
) -> ScheduleCreateMany:
    return ScheduleCreateMany(
        **{
            "schedules": [schedule_create_example, schedule_create_example],
            "telescope_id": mock_schedule_post_data["telescope_id"],
        }
    )


@pytest.fixture
def instrument_model_example(
    schedule_create_example: ScheduleCreate,
) -> InstrumentModel:
    return InstrumentModel(
        id=schedule_create_example.observations[0].instrument_id,
        telescope_id=schedule_create_example.telescope_id,
        field_of_view=InstrumentFOV.POLYGON,
    )


@pytest.fixture(params=["telescope_id", "name", "status", "date_range"])
def required_fields(request: pytest.FixtureRequest) -> Any:
    """
    Parameters pop in the create routine to trigger 422
    """
    return request.param
