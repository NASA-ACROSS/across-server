from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import anyio
import anyio.to_thread
import pytest
from across.tools.visibility.constraints import SunAngleConstraint

from across_server.core.enums.visibility_type import VisibilityType
from across_server.db.models import Instrument
from across_server.routes.v1.instrument.schemas import Instrument as InstrumentSchema
from across_server.routes.v1.instrument.service import InstrumentService
from across_server.routes.v1.tools.ephemeris.service import EphemerisService
from across_server.routes.v1.tools.visibility_calculator.schemas import (
    VisibilityReadParams,
)


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
    """Instrument model with constraint"""
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
    """Instrument model without constraints"""
    return InstrumentSchema(
        id=uuid4(),
        name="test_instrument",
        visibility_type=VisibilityType.EPHEMERIS,
        constraints=[],
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


@pytest.fixture(scope="function")
def mock_ephemeris_service() -> Generator[AsyncMock]:
    mock = AsyncMock(EphemerisService)

    mock.get = AsyncMock(return_value=None)
    yield mock


@pytest.fixture(scope="function")
def mock_instrument_service(
    fake_instrument_with_constraints: Instrument,
) -> Generator[AsyncMock]:
    mock = AsyncMock(InstrumentService)

    mock.get = AsyncMock(return_value=fake_instrument_with_constraints)
    yield mock


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


@pytest.fixture
def fake_visibility_read_params(
    fake_coordinates: tuple[float, float],
    fake_date_range: tuple[datetime, datetime],
) -> dict:
    return VisibilityReadParams(
        ra=fake_coordinates[0],
        dec=fake_coordinates[1],
        date_range_begin=fake_date_range[0],
        date_range_end=fake_date_range[1],
    ).model_dump()
