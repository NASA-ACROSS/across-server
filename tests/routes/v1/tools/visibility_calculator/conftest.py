from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import anyio
import anyio.to_thread
import pytest
from across.tools.visibility.constraints import SunAngleConstraint

from across_server.core.enums.visibility_type import VisibilityType
from across_server.routes.v1.instrument.schemas import Instrument as InstrumentSchema
from across_server.routes.v1.instrument.service import InstrumentService
from across_server.routes.v1.telescope.service import TelescopeService
from across_server.routes.v1.tools.ephemeris.service import EphemerisService


@pytest.fixture
def fake_sun_constraint() -> SunAngleConstraint:
    """Mock SunAngleConstraint"""
    return SunAngleConstraint(min_angle=45)


@pytest.fixture
def fake_instrument_id() -> UUID:
    """Sample instrument UUID"""
    return uuid4()


@pytest.fixture
def fake_observatory_id() -> UUID:
    """Sample observatory UUID"""
    return uuid4()


@pytest.fixture
def fake_telescope_id() -> UUID:
    """Sample telescope UUID"""
    return uuid4()


@pytest.fixture
def fake_date_range() -> tuple[datetime, datetime]:
    """Sample date range for testing"""
    return (datetime(2023, 1, 1), datetime(2023, 1, 2))


@pytest.fixture
def fake_coordinates() -> tuple[float, float]:
    """Sample RA/Dec coordinates"""
    return (10.0, 20.0)


@pytest.fixture
def fake_instrument_with_constraints(
    fake_sun_constraint: SunAngleConstraint,
) -> InstrumentSchema:
    """Instrument schema with constraints"""
    return InstrumentSchema(
        id=uuid4(),
        name="test_instrument",
        visibility_type=VisibilityType.EPHEMERIS,
        constraints=[fake_sun_constraint],
        short_name="test",
        created_on=datetime.now(),
    )


@pytest.fixture
def fake_instrument_without_constraints() -> InstrumentSchema:
    """Instrument schema without constraints"""
    return InstrumentSchema(
        id=uuid4(),
        name="test_instrument",
        visibility_type=VisibilityType.EPHEMERIS,
        constraints=None,
        short_name="test",
        created_on=datetime.now(),
    )


@pytest.fixture
def fake_async_result(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patches anyio.to_thread.run_sync with a AsyncMock"""
    mock_result = AsyncMock()
    monkeypatch.setattr(
        anyio.to_thread, "run_sync", AsyncMock(return_value=mock_result)
    )
    return mock_result


@pytest.fixture
def fake_ephemeris_service_get(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patches the EphemerisService.get return value with a MagicMock Ephemeris"""
    fake_service_get = AsyncMock(return_value=MagicMock())
    monkeypatch.setattr(EphemerisService, "__init__", MagicMock(return_value=None))
    monkeypatch.setattr(EphemerisService, "get", fake_service_get)
    return fake_service_get


@pytest.fixture
def fake_instrument_service_get(monkeypatch: pytest.MonkeyPatch) -> AsyncMock:
    """Patches the InstrumentService.get return value with a MagicMock Instrument"""
    fake_service_get = AsyncMock(return_value=MagicMock())

    monkeypatch.setattr(InstrumentService, "__init__", MagicMock(return_value=None))
    monkeypatch.setattr(InstrumentService, "get", fake_service_get)

    return fake_service_get


@pytest.fixture
def fake_telescope_service_get(
    monkeypatch: pytest.MonkeyPatch, fake_observatory_id: UUID
) -> AsyncMock:
    """Patches the TelescopeService.get return value with a MagicMock Telescope"""
    fake_telescope = MagicMock()
    fake_telescope.observatory_id = fake_observatory_id
    fake_telescope_get = AsyncMock(return_value=fake_telescope)

    monkeypatch.setattr(TelescopeService, "__init__", MagicMock(return_value=None))
    monkeypatch.setattr(TelescopeService, "get", fake_telescope_get)
    return fake_telescope_get


@pytest.fixture
def fake_instrument_schema_from_orm(
    monkeypatch: pytest.MonkeyPatch, fake_telescope_id: UUID
) -> MagicMock:
    """Patches the InstrumentSchema.from_orm return value with a MagicMock InstrumentSchema"""
    mock_instrument_schema = MagicMock()
    mock_instrument_schema.name = "Test Instrument"
    mock_instrument_schema.telescope = MagicMock()
    mock_instrument_schema.telescope.id = fake_telescope_id
    mock_instrument_schema.visibility_type = "ephemeris"

    monkeypatch.setattr(
        InstrumentSchema, "from_orm", MagicMock(return_value=mock_instrument_schema)
    )
    return mock_instrument_schema
