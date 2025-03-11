from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, mock_telescope_data):
        self.client = async_client
        self.endpoint = "/telescope/"
        self.get_data = mock_telescope_data


class TestTelescopeRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_telescope(self):
            """GET Should return created telescope when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.json()["name"] == self.get_data.name

        @pytest.mark.asyncio
        async def test_should_return_200(self):
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self):
            """GET many should return multiple telescopes when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())
            assert res.json()[0]["name"] == self.get_data.name

        @pytest.mark.asyncio
        async def test_many_should_return_200(self):
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
