from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI

from across_server.auth.strategies import auth_user_or_none, global_access
from across_server.routes.v1.observation_request.access import (
    observation_request_access,
    observation_request_status_access,
)


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
