from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import anyio.to_thread
import pytest

from across_server.core.enums.ephemeris_type import EphemerisType
from across_server.db.models import (
    EarthLocationParameters,
    JPLEphemerisParameters,
    Observatory,
    ObservatoryEphemerisType,
    SpiceKernelParameters,
    TLEParameters,
)
from across_server.routes.v1.observatory import schemas as observatory_schemas
from across_server.routes.v1.observatory.service import ObservatoryService
from across_server.routes.v1.tle.service import TLEService
from across_server.routes.v1.tools.ephemeris.service import EphemerisService


@pytest.fixture
def fake_observatory_id() -> UUID:
    """Test observatory ID"""
    return uuid4()


@pytest.fixture
def fake_date_range() -> dict[str, datetime]:
    """Test date range"""
    return {"begin": datetime(2023, 1, 1), "end": datetime(2023, 1, 2)}


@pytest.fixture
def fake_operational_date_range() -> observatory_schemas.DateRange:
    """Operational date range for observatory"""
    return observatory_schemas.DateRange(
        begin=datetime(2023, 6, 1), end=datetime(2023, 12, 31)
    )


@pytest.fixture
def fake_tle_parameters(fake_observatory_id: UUID) -> TLEParameters:
    """TLE parameters"""
    return TLEParameters(
        observatory_id=fake_observatory_id, norad_id=12345, norad_satellite_name="Test"
    )


@pytest.fixture
def fake_jpl_parameters() -> JPLEphemerisParameters:
    """JPL parameters"""
    return JPLEphemerisParameters(naif_id=399)


@pytest.fixture
def fake_spice_parameters() -> SpiceKernelParameters:
    """SPICE parameters"""
    return SpiceKernelParameters(spice_kernel_url="http://test.com", naif_id=399)


@pytest.fixture
def fake_ground_parameters() -> EarthLocationParameters:
    """Ground parameters"""
    return EarthLocationParameters(longitude=0.0, latitude=0.0, height=0.0)


@pytest.fixture
def fake_tle_ephemeris_type(
    fake_tle_parameters: TLEParameters,
) -> ObservatoryEphemerisType:
    """TLE ephemeris type"""
    return ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.TLE, priority=1, parameters=fake_tle_parameters
    )


@pytest.fixture
def fake_jpl_ephemeris_type(
    fake_jpl_parameters: JPLEphemerisParameters,
) -> ObservatoryEphemerisType:
    """JPL ephemeris type"""
    return ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.JPL, priority=2, parameters=fake_jpl_parameters
    )


@pytest.fixture
def fake_spice_ephemeris_type(
    fake_spice_parameters: SpiceKernelParameters,
) -> ObservatoryEphemerisType:
    """SPICE ephemeris type"""
    return ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.SPICE, priority=3, parameters=fake_spice_parameters
    )


@pytest.fixture
def fake_ground_ephemeris_type(
    fake_ground_parameters: EarthLocationParameters,
) -> ObservatoryEphemerisType:
    """Ground ephemeris type"""
    return ObservatoryEphemerisType(
        ephemeris_type=EphemerisType.GROUND,
        priority=4,
        parameters=fake_ground_parameters,
    )


@pytest.fixture
def fake_observatory_model(
    fake_observatory_id: UUID,
    fake_tle_ephemeris_type: ObservatoryEphemerisType,
) -> Observatory:
    """Mock observatory model. This needs to be an actual Observatory db model"""
    mock_model = Observatory(
        name="Test Observatory",
        short_name="TEST",
        type="SPACE_BASED",
        id=fake_observatory_id,
        ephemeris_types=[fake_tle_ephemeris_type],
        created_on=datetime(2023, 1, 1),
    )
    return mock_model


@pytest.fixture
def fake_observatory_model_no_ephemeris(fake_observatory_id: UUID) -> Observatory:
    """Fake observatory model with no ephemeris types"""
    mock_model = Observatory(
        name="Test Observatory",
        short_name="TEST",
        type="SPACE_BASED",
        id=fake_observatory_id,
        ephemeris_types=[],
        created_on=datetime(2023, 1, 1),
    )
    return mock_model


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
def fake_tle_data(todays_epoch_yyddd: str) -> dict:
    return {
        "norad_id": 12345,
        "satellite_name": "TEST",
        "tle1": f"1 28485U 04047A   {todays_epoch_yyddd}  .00027471  00000+0  86373-3 0  9997",
        "tle2": "2 28485  20.5557 285.8116 0006385  93.6070 266.5099 15.31053389110064",
    }


@pytest.fixture
def mock_ephemeris_result(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patches anyio.to_thread.run_sync with a AsyncMock"""
    mock_ephemeris_result = MagicMock()
    monkeypatch.setattr(
        anyio.to_thread, "run_sync", AsyncMock(return_value=mock_ephemeris_result)
    )
    return mock_ephemeris_result


@pytest.fixture
def fake_tle_service_get(
    monkeypatch: pytest.MonkeyPatch, fake_tle_data: dict
) -> AsyncMock:
    """"""
    mock_tle_model = MagicMock()
    mock_tle_model.__dict__ = fake_tle_data

    fake_tle_get = AsyncMock(return_value=mock_tle_model)

    monkeypatch.setattr(TLEService, "__init__", MagicMock(return_value=None))
    monkeypatch.setattr(TLEService, "get", fake_tle_get)

    return fake_tle_get


@pytest.fixture
def fake_observatory_service_get(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """"""
    fake_observatory_get = AsyncMock(return_value=None)
    monkeypatch.setattr(ObservatoryService, "__init__", MagicMock(return_value=None))
    monkeypatch.setattr(ObservatoryService, "get", fake_observatory_get)
    return fake_observatory_get


@pytest.fixture
def fake_ephemeris_service_get(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    fake_get_result = AsyncMock(return_value=None)
    monkeypatch.setattr(EphemerisService, "_get_tle_ephem", fake_get_result)
    return fake_get_result
