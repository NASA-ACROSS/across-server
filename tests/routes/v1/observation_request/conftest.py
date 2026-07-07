from collections.abc import Generator
from datetime import datetime
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from pydantic import BaseModel

from across_server.auth.enums import PrincipalType
from across_server.auth.schemas import AuthUser, Group
from across_server.auth.strategies import auth_user_or_none, global_access
from across_server.core.schemas import PaginationParams
from across_server.db import models
from across_server.routes.v1.observation_request.access import (
    observation_request_access,
    observation_request_status_access,
)


class FakeObservationRequestReadParams(PaginationParams):
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
    proposal_name: str | None = None
    proposal_code: str | None = None
    proposal_ids: list[str] | None = None
    is_too: bool | None = None
    parent_id: UUID | None = None


class FakeObservationHistoryParams(PaginationParams):
    observation_request_id: UUID


class FakeObservationRequestCreate(BaseModel):
    id: str = "fake-obs-request-id"
    instrument_id: str = "fake-obs-request-instrument-id"

    def to_orm(self, created_by_id: UUID) -> "FakeObservationRequestCreate":
        return self


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
        status="PENDING",
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
        created_by_id=uuid4(),
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
def mock_observation_request_access() -> Generator[MagicMock]:
    mock = MagicMock(observation_request_access)
    mock.id = 1

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_observation_request_access: MagicMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            auth_user_or_none: lambda: mock_observation_request_access,
            global_access: lambda: mock_observation_request_access,
            observation_request_access: lambda: mock_observation_request_access,
            observation_request_status_access: lambda: mock_observation_request_access,
        }
    ):
        yield overrider
