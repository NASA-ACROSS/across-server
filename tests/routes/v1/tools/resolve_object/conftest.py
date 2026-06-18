from collections.abc import Generator
from typing import Any
from unittest.mock import AsyncMock

import pytest
from astropy.coordinates import SkyCoord  # type: ignore[import-untyped]
from fastapi import FastAPI

from across_server.core.schemas import Coordinate
from across_server.routes.v1.tools.resolve_object.schemas import (
    NameResolver,
    NameResolverRead,
)
from across_server.routes.v1.tools.resolve_object.service import NameResolveService


@pytest.fixture()
def mock_coordinate() -> Coordinate:
    return Coordinate(ra=123.45, dec=-43.21)


@pytest.fixture()
def mock_null_coordinate() -> Coordinate:
    return Coordinate(ra=None, dec=None)


@pytest.fixture()
def mock_skycoord() -> SkyCoord:
    return SkyCoord(350.866461, 58.811779, unit="deg")


@pytest.fixture()
def mock_resolve_params() -> dict:
    return NameResolverRead(object_name="Cas A").model_dump()


@pytest.fixture()
def mock_resolve_input() -> NameResolverRead:
    return NameResolverRead(object_name="Cas A")


@pytest.fixture()
def mock_ztf_resolve_input() -> NameResolverRead:
    return NameResolverRead(object_name="ZTFsandytreedome")


@pytest.fixture()
def mock_resolve_data() -> NameResolver:
    return NameResolver.model_validate(
        {
            "ra": 350.866461,
            "dec": 58.811779,
            "resolver": "CDS",
        }
    )


@pytest.fixture(scope="function")
def mock_name_resolve_service(
    mock_resolve_data: NameResolver,
) -> Generator[AsyncMock]:
    mock = AsyncMock(NameResolveService)

    mock.resolve = AsyncMock(return_value=mock_resolve_data)

    yield mock


@pytest.fixture(scope="function", autouse=True)
def dep_override(
    app: FastAPI, fastapi_dep: Any, mock_name_resolve_service: AsyncMock
) -> Generator[None, None, None]:
    overrider = fastapi_dep(app)

    with overrider.override(
        {
            NameResolveService: lambda: mock_name_resolve_service,
        }
    ):
        yield overrider
