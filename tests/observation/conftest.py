from datetime import datetime
from uuid import uuid4

import pytest
from across.tools import WavelengthBandpass
from across.tools import enums as tools_enums

from across_server.core.enums.observation_status import ObservationStatus
from across_server.core.enums.observation_type import ObservationType
from across_server.core.schemas.coordinate import Coordinate
from across_server.core.schemas.date_range import DateRange
from across_server.db.models import Observation as ObservationModel
from across_server.routes.observation.schemas import ObservationCreate


@pytest.fixture
def mock_observation_data() -> dict:
    return {
        "instrument_id": str(uuid4()),
        "schedule_id": str(uuid4()),
        "object_name": "test object",
        "pointing_position": {"ra": 123.456, "dec": -87.65},
        "date_range": {"begin": "2024-12-16 11:00:00", "end": "2024-12-17 11:00:00"},
        "external_observation_id": "test-external-obsid",
        "type": "imaging",
        "status": "planned",
        "created_on": "2024-12-16 00:00:00",
        "bandpass": {"min": 2000, "max": 4000, "unit": "angstrom"},
    }


@pytest.fixture
def mock_observation_model() -> ObservationModel:
    return ObservationModel(
        id=uuid4(),
        instrument_id=uuid4(),
        schedule_id=uuid4(),
        object_name="test object",
        pointing_ra=123.456,
        pointing_dec=-87.65,
        date_range_begin=datetime(2024, 12, 16, 11, 0),
        date_range_end=datetime(2024, 12, 17, 11, 0),
        external_observation_id="test-external-obsid",
        type="imaging",
        status="planned",
        created_on=datetime(2024, 12, 16),
        min_wavelength=2000,
        max_wavelength=4000,
    )


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
