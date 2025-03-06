from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from across_server.db.models import Telescope as TelescopeModel
from across_server.routes.telescope.service import TelescopeService


@pytest.fixture()
def mock_telescope_data():
    return TelescopeModel(
        id=uuid4(), name="Test Telescope", short_name="TT", created_on=datetime.now()
    )


@pytest.fixture(scope="function")
def mock_telescope_service(mock_telescope_data):
    mock = AsyncMock(TelescopeService)

    mock.get = AsyncMock(return_value=mock_telescope_data)
    mock.get_many = AsyncMock(return_value=[mock_telescope_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(app, fastapi_dep, mock_telescope_service):
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            TelescopeService: lambda: mock_telescope_service,
        }
    ):
        yield overrider
