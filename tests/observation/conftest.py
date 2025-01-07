from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from across_server.routes.observation.service import ObservationService


class MockObservationSchema:
    @classmethod
    def to_orm(cls):
        return cls()

    def __init__(self, **kwargs):
        self.model_config = {"return_schema": self.__class__}


@pytest.fixture(scope="function")
def mock_observation():
    return MockObservationSchema()


@pytest.fixture
def mock_observation_data():
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
    }


@pytest.fixture(scope="function")
def mock_observation_service(mock_observation_data):
    mock = AsyncMock(ObservationService)

    returned_mock_observation = mock_observation_data
    returned_mock_observation["id"] = str(uuid4())
    returned_mock_observation["description"] = "the returned observation"

    mock.create = AsyncMock(return_value=returned_mock_observation)
    yield mock


@pytest.fixture(scope="function")
def mock_db_session():
    mock = AsyncMock(AsyncSession)
    mock.add = Mock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app,
    fastapi_dep,
    mock_observation_service,
):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ObservationService: lambda: mock_observation_service,
        }
    ):
        yield overrider
