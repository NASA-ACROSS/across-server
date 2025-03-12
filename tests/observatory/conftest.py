from collections.abc import Generator
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from fastapi import FastAPI

from across_server.db.models import Observatory as ObservatoryModel
from across_server.routes.observatory.service import ObservatoryService


@pytest.fixture()
def mock_observatory_data() -> ObservatoryModel:
    return ObservatoryModel(
        id=uuid4(),
        name="Test Observatory",
        short_name="TO",
        observatory_type="GROUND_BASED",
        created_on=datetime.now(),
    )


@pytest.fixture(scope="function")
def mock_observatory_service(
    mock_observatory_data: ObservatoryModel,
) -> Generator[AsyncMock]:
    mock = AsyncMock(ObservatoryService)

    mock.get = AsyncMock(return_value=mock_observatory_data)
    mock.get_many = AsyncMock(return_value=[mock_observatory_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: Any, mock_observatory_service: AsyncMock
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            ObservatoryService: lambda: mock_observatory_service,
        }
    ):
        yield overrider
