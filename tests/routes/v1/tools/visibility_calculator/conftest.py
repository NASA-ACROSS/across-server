from collections.abc import Generator
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from across.tools.visibility.constraints import SunAngleConstraint
from fastapi import FastAPI

from across_server.core.enums.visibility_type import VisibilityType
from across_server.db.models import Instrument, Telescope
from across_server.routes.v1.instrument.schemas import Instrument as InstrumentSchema
from across_server.routes.v1.instrument.service import InstrumentService
from across_server.routes.v1.telescope.service import TelescopeService
from across_server.routes.v1.tools.ephemeris.service import EphemerisService
from across_server.routes.v1.tools.visibility_calculator.schemas import (
    JointVisibilityReadParams,
    VisibilityReadParams,
)
from across_server.routes.v1.tools.visibility_calculator.service import (
    VisibilityCalculatorService,
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
def fake_ephemeris_visibility_result() -> MagicMock:
    mock = MagicMock()
    mock.model_dump.return_value = {"visibility_windows": []}
    mock.instrument_id = uuid4()

    return mock


@pytest.fixture
def fake_joint_visibility_result() -> MagicMock:
    mock = MagicMock()
    mock.model_dump.return_value = {"visibility_windows": []}
    mock.instrument_ids = [uuid4()]

    return mock


@pytest.fixture(scope="function")
def mock_ephemeris_service() -> Generator[AsyncMock]:
    mock = AsyncMock(EphemerisService)

    mock.get = AsyncMock(return_value=None)
    yield mock


@pytest.fixture(scope="function")
def mock_instrument_service(
    mock_instrument_data: Instrument,
) -> Generator[AsyncMock]:
    mock = AsyncMock(InstrumentService)

    mock.get = AsyncMock(return_value=mock_instrument_data)
    yield mock


@pytest.fixture(scope="function")
def mock_telescope_service(mock_telescope_data: Telescope) -> Generator[AsyncMock]:
    mock = AsyncMock(TelescopeService)

    mock.get = AsyncMock(return_value=mock_telescope_data)
    yield mock


@pytest.fixture(scope="function")
def mock_visibility_calculator_service(
    fake_ephemeris_visibility_result: MagicMock,
    fake_joint_visibility_result: MagicMock,
) -> Generator[AsyncMock]:
    mock = AsyncMock(VisibilityCalculatorService)

    mock.calculate_windows = AsyncMock(return_value=fake_ephemeris_visibility_result)
    mock.find_joint_visibility = AsyncMock(return_value=fake_joint_visibility_result)
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


@pytest.fixture
def fake_joint_visibility_read_params(
    fake_coordinates: tuple[float, float],
    fake_date_range: tuple[datetime, datetime],
) -> dict:
    return JointVisibilityReadParams(
        ra=fake_coordinates[0],
        dec=fake_coordinates[1],
        date_range_begin=fake_date_range[0],
        date_range_end=fake_date_range[1],
        instrument_ids=[uuid4(), uuid4()],
    ).model_dump()


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_instrument_service: AsyncMock,
    mock_telescope_service: AsyncMock,
    mock_visibility_calculator_service: AsyncMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            InstrumentService: lambda: mock_instrument_service,
            TelescopeService: lambda: mock_telescope_service,
            VisibilityCalculatorService: lambda: mock_visibility_calculator_service,
        }
    ):
        yield overrider
