from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from pydantic import BaseModel

from across_server.auth.enums import PrincipalType
from across_server.auth.schemas import AuthUser, Group
from across_server.auth.strategies import (
    auth_user_or_none,
    authenticate_jwt,
    global_access,
)
from across_server.core.enums import ObservationRequestStatus
from across_server.core.schemas import (
    Coordinate,
    NullableEndDateRange,
    PaginationParams,
    UnitValue,
)
from across_server.db import models
from across_server.routes.v1.observation_request import schemas as obs_schemas
from across_server.routes.v1.observation_request.access import (
    observation_request_access,
    observation_request_status_access,
)
from across_server.routes.v1.observation_request.service import (
    ObservationRequestService,
)


class FakeObservationRequestReadParams(PaginationParams):
    observatory_names: list[str] | None = None
    observatory_ids: list[UUID] | None = None
    telescope_names: list[str] | None = None
    telescope_ids: list[str] | None = None
    instrument_names: list[str] | None = None
    instrument_ids: list[str] | None = None
    object_name: str | None = None
    object_cone_search_ra: float | None = None
    object_cone_search_dec: float | None = None
    object_cone_search_radius: float | None = None
    begin_date: datetime | None = None
    end_date: datetime | None = None
    status: Any | None = None
    proposal_name: str | None = None
    proposal_code: str | None = None
    proposal_ids: list[str] | None = None
    is_too: bool | None = None
    parent_id: UUID | None = None
    include_history: bool = False


class FakeObservationHistoryParams(PaginationParams):
    observation_request_id: UUID


class FakeObservationRequestCreate(BaseModel):
    id: str = "fake-obs-request-id"
    instrument_id: str = "fake-obs-request-instrument-id"
    parent_id: UUID | None = None
    proposal_name: str | None = None
    proposal_code: str | None = None

    def to_orm(self) -> MagicMock:
        return MagicMock()


class FakeObservationRequestCreateMany:
    def __init__(self, observation_requests: list) -> None:
        self.observation_requests = observation_requests


@pytest.fixture(autouse=True)
def fake_auth_user(fake_group: models.Group) -> AuthUser:
    return AuthUser(
        id=uuid4(),
        groups=[Group(id=fake_group.id, scopes=["mock_scope"], is_admin=False)],
        scopes=["mock_scope"],
        first_name="Mock",
        last_name="User",
        username="mockuser",
        type=PrincipalType.USER,
    )


@pytest.fixture(autouse=True)
def fake_observation_request(
    mock_instrument_data: models.Instrument,
) -> models.ObservationRequest:
    return models.ObservationRequest(
        id=uuid4(),
        status="pending",
        science_justification="test",
        object_ra=123.45,
        object_dec=-76.54,
        object_name="Test Object",
        object_brightness=12.34,
        object_brightness_unit="AB_mag",
        date_range_begin=datetime(2026, 6, 25),
        exposure_time=3600.0,
        parent_id=uuid4(),
        instrument=mock_instrument_data,
        instrument_id=mock_instrument_data.id,
        created_by_id=uuid4(),
        created_on=datetime(2026, 6, 25),
        anonymize=False,
        is_too=False,
    )


@pytest.fixture(autouse=True)
def mock_observation_request_read_params() -> FakeObservationRequestReadParams:
    return FakeObservationRequestReadParams()


@pytest.fixture(autouse=True)
def mock_observation_request_create() -> FakeObservationRequestCreate:
    return FakeObservationRequestCreate()


@pytest.fixture(autouse=True)
def mock_observation_history_params() -> FakeObservationHistoryParams:
    return FakeObservationHistoryParams(observation_request_id=uuid4())


@pytest.fixture
def fake_observation_request_schema() -> obs_schemas.ObservationRequest:
    _id = uuid4()
    return obs_schemas.ObservationRequest(
        id=_id,
        parent_id=_id,
        science_justification="test",
        object_name="Test Object",
        object_coordinates=Coordinate(ra=123.45, dec=-76.54),
        object_brightness=UnitValue(value=12.34, unit="AB_mag"),
        observation_window=NullableEndDateRange(begin=datetime(2026, 6, 25), end=None),
        exposure_time=3600.0,
        anonymize=False,
        is_too=False,
        instrument_id=_id,
        status=ObservationRequestStatus.PENDING,
        status_reason="Awaiting review",
        created_on=datetime(2026, 6, 25),
        created_by_id=_id,
        modified_on=None,
        modified_by_id=None,
    )


@pytest.fixture
def mock_observation_request_create_many(
    mock_observation_request_create: Any,
) -> FakeObservationRequestCreateMany:
    return FakeObservationRequestCreateMany(
        observation_requests=[mock_observation_request_create]
    )


@pytest.fixture
def mock_observation_request_service(
    fake_observation_request_schema: obs_schemas.ObservationRequest,
) -> AsyncMock:
    mock = AsyncMock(ObservationRequestService)
    _id = uuid4()
    mock.get = AsyncMock(return_value=fake_observation_request_schema)
    mock.get_many = AsyncMock(return_value=[(fake_observation_request_schema, 1)])
    mock.create = AsyncMock(return_value=_id)
    mock.create_many = AsyncMock(return_value=[_id])
    mock.modify = AsyncMock(return_value=_id)
    mock.update_status = AsyncMock(return_value=_id)
    return mock


@pytest.fixture
def mock_observation_request_access() -> Generator[MagicMock]:
    mock = MagicMock(observation_request_access)
    mock.id = 1

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_observation_request_access: MagicMock,
    mock_observation_request_service: AsyncMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            auth_user_or_none: lambda: mock_observation_request_access,
            authenticate_jwt: lambda: mock_observation_request_access,
            global_access: lambda: mock_observation_request_access,
            observation_request_access: lambda: mock_observation_request_access,
            observation_request_status_access: lambda: mock_observation_request_access,
            ObservationRequestService: lambda: mock_observation_request_service,
        }
    ):
        yield overrider
