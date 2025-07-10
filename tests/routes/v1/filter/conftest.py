from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI

from across_server.db.models import Filter
from across_server.routes.v1.filter.service import FilterService


@pytest.fixture(scope="function")
def mock_filter_service(mock_filter_data: Filter) -> Generator[AsyncMock]:
    mock = AsyncMock(FilterService)

    mock.get = AsyncMock(return_value=mock_filter_data)
    mock.get_many = AsyncMock(return_value=[mock_filter_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: MagicMock, mock_filter_service: AsyncMock
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            FilterService: lambda: mock_filter_service,
        }
    ):
        yield overrider
