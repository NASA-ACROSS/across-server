import pytest
from uuid import uuid4
from unittest.mock import AsyncMock, Mock
from across_server.routes.observation.service import ObservationService
from sqlalchemy.ext.asyncio import AsyncSession


class MockObservationSchema:
    @staticmethod
    def to_orm():
        pass

    @classmethod
    def from_orm(cls, data):
        return cls()
    

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
        "date_range": {
            "begin": "2024-12-16 11:00:00", 
            "end": "2024-12-17 11:00:00"
        },
        "external_observation_id": "test-external-obsid",
        "type": "imaging",
        "status": "planned"
    }

@pytest.fixture(scope="function")
def mock_observation_service(mock_observation_data):
    mock = AsyncMock(ObservationService)

    returned_mock_observation = mock_observation_data
    returned_mock_observation["description"] = "the returned observation"
    
    mock.create = AsyncMock(
        return_value = returned_mock_observation
    )
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