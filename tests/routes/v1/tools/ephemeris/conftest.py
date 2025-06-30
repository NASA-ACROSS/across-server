from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest

from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.routes.v1.observatory import schemas as observatory_schemas


@pytest.fixture
def mock_db() -> AsyncMock:
    """Mock database session"""
    return AsyncMock()


@pytest.fixture
def test_observatory_id() -> UUID:
    """Test observatory ID"""
    return uuid4()


@pytest.fixture
def test_date_range() -> dict[str, datetime]:
    """Test date range"""
    return {"begin": datetime(2023, 1, 1), "end": datetime(2023, 1, 2)}


@pytest.fixture
def operational_date_range() -> observatory_schemas.DateRange:
    """Operational date range for observatory"""
    return observatory_schemas.DateRange(
        begin=datetime(2023, 6, 1), end=datetime(2023, 12, 31)
    )


@pytest.fixture
def tle_parameters() -> observatory_schemas.TLEParameters:
    """TLE parameters"""
    return observatory_schemas.TLEParameters(
        norad_id=12345, norad_satellite_name="Test"
    )


@pytest.fixture
def jpl_parameters() -> observatory_schemas.JPLParameters:
    """JPL parameters"""
    return observatory_schemas.JPLParameters(naif_id=399)


@pytest.fixture
def spice_parameters() -> observatory_schemas.SPICEParameters:
    """SPICE parameters"""
    return observatory_schemas.SPICEParameters(
        spice_kernel_url="http://test.com", naif_id=399
    )


@pytest.fixture
def ground_parameters() -> observatory_schemas.GroundParameters:
    """Ground parameters"""
    return observatory_schemas.GroundParameters(longitude=0.0, latitude=0.0, height=0.0)


@pytest.fixture
def tle_ephemeris_type(
    tle_parameters: observatory_schemas.TLEParameters,
) -> observatory_schemas.ObservatoryEphemerisType:
    """TLE ephemeris type"""
    return observatory_schemas.ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.TLE, priority=1, parameters=tle_parameters
    )


@pytest.fixture
def jpl_ephemeris_type(
    jpl_parameters: observatory_schemas.JPLParameters,
) -> observatory_schemas.ObservatoryEphemerisType:
    """JPL ephemeris type"""
    return observatory_schemas.ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.JPL, priority=2, parameters=jpl_parameters
    )


@pytest.fixture
def spice_ephemeris_type(
    spice_parameters: observatory_schemas.SPICEParameters,
) -> observatory_schemas.ObservatoryEphemerisType:
    """SPICE ephemeris type"""
    return observatory_schemas.ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.SPICE, priority=3, parameters=spice_parameters
    )


@pytest.fixture
def ground_ephemeris_type(
    ground_parameters: observatory_schemas.GroundParameters,
) -> observatory_schemas.ObservatoryEphemerisType:
    """Ground ephemeris type"""
    return observatory_schemas.ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.GROUND, priority=4, parameters=ground_parameters
    )


@pytest.fixture
def mock_observatory_model(
    test_observatory_id: UUID,
    tle_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
) -> MagicMock:
    """Mock observatory model"""
    mock_model = MagicMock()
    mock_model.__dict__ = {
        "name": "Test Observatory",
        "short_name": "TEST",
        "type": "SPACE_BASED",
        "id": test_observatory_id,
        "operational": None,
        "ephemeris_types": [tle_ephemeris_type],
        "created_on": datetime.now(),
    }
    return mock_model


@pytest.fixture
def mock_observatory_model_with_operational(
    test_observatory_id: UUID,
    tle_ephemeris_type: observatory_schemas.ObservatoryEphemerisType,
    operational_date_range: observatory_schemas.DateRange,
) -> MagicMock:
    """Mock observatory model with operational range"""
    mock_model = MagicMock()
    mock_model.__dict__ = {
        "name": "Test Observatory",
        "short_name": "TEST",
        "type": "SPACE_BASED",
        "id": test_observatory_id,
        "operational_begin_date": operational_date_range.begin,
        "operational_end_date": operational_date_range.end,
        "ephemeris_types": [tle_ephemeris_type],
        "created_on": datetime(2023, 1, 1),
    }
    return mock_model


@pytest.fixture
def mock_observatory_model_no_ephemeris(test_observatory_id: UUID) -> MagicMock:
    """Mock observatory model with no ephemeris types"""
    mock_model = MagicMock()
    mock_model.__dict__ = {
        "name": "Test Observatory",
        "short_name": "TEST",
        "type": "SPACE_BASED",
        "id": test_observatory_id,
        "ephemeris_types": [],
        "created_on": datetime(2023, 1, 1),
    }
    return mock_model


@pytest.fixture
def mock_ephemeris() -> MagicMock:
    """Mock ephemeris result"""
    return MagicMock()


@pytest.fixture(scope="function")
def todays_epoch() -> datetime:
    return datetime.now()


@pytest.fixture(scope="function")
def todays_epoch_yyddd(todays_epoch: datetime) -> str:
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
        "satellite_name": "TEST",
        "tle1": f"1 28485U 04047A   {todays_epoch_yyddd}  .00027471  00000+0  86373-3 0  9997",
        "tle2": "2 28485  20.5557 285.8116 0006385  93.6070 266.5099 15.31053389110064",
    }
