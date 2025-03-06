from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, mock_observatory_data):
        self.client = async_client
        self.endpoint = "/observatory/"
        self.get_data = mock_observatory_data


class TestObservatoryRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observatory(self):
            """GET Should return created observatory when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.json()["name"] == "Test Observatory"

        @pytest.mark.asyncio
        async def test_should_return_200(self):
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self):
            """GET many should return multiple observatories when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())
            assert res.json()[0]["name"] == "Test Observatory"

        @pytest.mark.asyncio
        async def test_many_should_return_200(self):
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
