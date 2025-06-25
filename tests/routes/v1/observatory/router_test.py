from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.db.models import Observatory as ObservatoryModel
from across_server.routes.v1.observatory.schemas import Observatory


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self, async_client: AsyncClient, mock_observatory_data: ObservatoryModel
    ) -> None:
        self.client = async_client
        self.endpoint = "/observatory/"
        self.get_data = mock_observatory_data


class TestObservatoryRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observatory(self) -> None:
            """GET Should return created observatory when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert Observatory.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many should return multiple when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())

        @pytest.mark.asyncio
        async def test_many_should_return_many_telescopes(self) -> None:
            """GET many should return multiple observatories when successful"""
            res = await self.client.get(self.endpoint)
            assert all([Observatory.model_validate(json) for json in res.json()])

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
