from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.db.models import Observatory as ObservatoryModel
from across_server.routes.observatory.service import ObservatoryService


@pytest.fixture()
def mock_observatory_data():
    return ObservatoryModel(
        id=uuid4(),
        name="Test Observatory",
        short_name="TO",
        observatory_type="GROUND_BASED",
        created_on=datetime.now(),
    )


@pytest.fixture(scope="function")
def mock_observatory_service(mock_observatory_data):
    mock = AsyncMock(ObservatoryService)

    mock.get = AsyncMock(return_value=mock_observatory_data)
    mock.get_many = AsyncMock(return_value=[mock_observatory_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(app, fastapi_dep, mock_observatory_service):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ObservatoryService: lambda: mock_observatory_service,
        }
    ):
        yield overrider
