from collections.abc import Generator
from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest
from across.tools.visibility.constraints import SunAngleConstraint

from across_server.core.enums.visibility_type import VisibilityType
from across_server.routes.v1.instrument.schemas import Instrument as InstrumentSchema


@pytest.fixture
def mock_sun_constraint() -> SunAngleConstraint:
    """Mock SunAngleConstraint"""
    return SunAngleConstraint(min_angle=45)


@pytest.fixture
def mock_db() -> AsyncMock:
    """Mock database"""
    return AsyncMock()


@pytest.fixture
def sample_instrument_id() -> UUID:
    """Sample instrument UUID"""
    return uuid4()


@pytest.fixture
def sample_observatory_id() -> UUID:
    """Sample observatory UUID"""
    return uuid4()


@pytest.fixture
def sample_telescope_id() -> UUID:
    """Sample telescope UUID"""
    return uuid4()


@pytest.fixture
def sample_date_range() -> tuple[datetime, datetime]:
    """Sample date range for testing"""
    return (datetime(2023, 1, 1), datetime(2023, 1, 2))


@pytest.fixture
def sample_coordinates() -> tuple[float, float]:
    """Sample RA/Dec coordinates"""
    return (10.0, 20.0)


@pytest.fixture
def instrument_with_constraints(
    mock_sun_constraint: SunAngleConstraint,
) -> InstrumentSchema:
    """Instrument schema with constraints"""
    return InstrumentSchema(
        id=uuid4(),
        name="test_instrument",
        visibility_type=VisibilityType.EPHEMERIS,
        constraints=[mock_sun_constraint],
        short_name="test",
        created_on=datetime.now(),
    )


@pytest.fixture
def instrument_without_constraints() -> InstrumentSchema:
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
def mock_ephemeris_mocks() -> Generator[tuple[AsyncMock, AsyncMock, AsyncMock]]:
    """Mock ephemeris-related services and functions"""
    mock_ephemeris_service = AsyncMock()
    mock_compute_visibility = AsyncMock()
    mock_visibility_result = AsyncMock()

    mock_ephemeris_service.get.return_value = AsyncMock()

    with (
        patch(
            "across_server.routes.v1.tools.visibility_calculator.service.EphemerisService",
            return_value=mock_ephemeris_service,
        ),
        patch(
            "across_server.routes.v1.tools.visibility_calculator.service.compute_ephemeris_visibility",
            mock_compute_visibility,
        ),
        patch(
            "anyio.to_thread.run_sync",
            new=AsyncMock(return_value=mock_visibility_result),
        ),
    ):
        yield mock_ephemeris_service, mock_compute_visibility, mock_visibility_result
