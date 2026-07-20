from collections.abc import Callable, Generator
from unittest.mock import AsyncMock
from uuid import UUID

import pytest
from fastapi import FastAPI

from across_server.auth.enums import PrincipalType
from across_server.auth.schemas import AuthUser
from across_server.routes.v1.telescope.service import TelescopeService


@pytest.fixture(scope="function")
def mock_telescope_service(mock_telescope_data: None) -> Generator[AsyncMock]:
    mock = AsyncMock(TelescopeService)

    mock.get = AsyncMock(return_value=mock_telescope_data)
    mock.get_many = AsyncMock(return_value=[mock_telescope_data])

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: Callable, mock_telescope_service: AsyncMock
) -> Generator:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            TelescopeService: lambda: mock_telescope_service,
        }
    ):
        yield overrider


@pytest.fixture()
def fake_auth_user() -> AuthUser:
    return AuthUser(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        scopes=[],
        groups=[],
        type=PrincipalType.USER,
    )
