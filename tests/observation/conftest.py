from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

from across_server.routes.observation.service import ObservationService
from across_server.routes.schedule.access import schedule_access


class MockObservationSchema:
    @classmethod
    def to_orm(cls) -> "MockObservationSchema":
        return cls()

    def __init__(self, **kwargs: Any) -> None:
        self.return_schema = self.__class__


@pytest.fixture(scope="function")
def mock_observation() -> MockObservationSchema:
    return MockObservationSchema()


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


@pytest.fixture(scope="function")
def mock_observation_service(mock_observation_data: dict) -> Generator[AsyncMock]:
    mock = AsyncMock(ObservationService)

    returned_mock_observation = mock_observation_data
    returned_mock_observation["id"] = str(uuid4())
    returned_mock_observation["description"] = "the returned observation"

    mock.create = AsyncMock(return_value=returned_mock_observation)
    yield mock


@pytest.fixture
def mock_schedule_access() -> Generator[MagicMock]:
    mock = MagicMock(schedule_access)

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI,
    fastapi_dep: MagicMock,
    mock_observation_service: MagicMock,
    mock_schedule_access: MagicMock,
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ObservationService: lambda: mock_observation_service,
            schedule_access: lambda: mock_schedule_access,
        }
    ):
        yield overrider
