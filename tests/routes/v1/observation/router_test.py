from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.observation.schemas import Observation


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self, async_client: AsyncClient, mock_observation_data: None
    ) -> None:
        self.client = async_client
        self.endpoint = "/observation/"
        self.get_data = mock_observation_data


class SetupMany:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self, async_client: AsyncClient, mock_observation_many: None
    ) -> None:
        self.client = async_client
        self.endpoint = "/observation/"
        self.get_data = mock_observation_many


class TestObservationRouterGet:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observation(self) -> None:
            """GET Should return created observation when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert Observation.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestGetMany(SetupMany):
        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many should return multiple when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())

        @pytest.mark.asyncio
        async def test_many_should_return_many_observations(self) -> None:
            """GET many should return multiple observations when successful"""
            res = await self.client.get(self.endpoint)
            assert all([Observation.model_validate(obs) for obs in res.json()["items"]])

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
