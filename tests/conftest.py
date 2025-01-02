import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from across_server import main


@pytest.fixture(scope="module")
def app():
    return main.app


@pytest_asyncio.fixture(scope="module", autouse=True)
async def async_client(app: FastAPI):
    host, port = "127.0.0.1", 9000

    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(
            app=app,
            client=(host, port),
        ),
        base_url="http://test",
    )

    async with client:
        yield client


# @pytest.fixture
# def dep_overrider(request, app, fastapi_dep):
#     parametrized = getattr(request, "param", None)

#     overrider = fastapi_dep(app, request) if parametrized else fastapi_dep(app)

#     with overrider:
#         yield overrider
