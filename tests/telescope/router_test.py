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

    def is_telescope(self, response_json: dict):
        """Method to validate if the api return is consistent with expected json keys"""
        telescope_return_keys = [
            "id",
            "name",
            "short_name",
            "created_on",
            "observatory",
        ]
        return all(key in response_json for key in telescope_return_keys)


class TestTelescopeRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_telescope(self):
            """GET Should return created telescope when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert self.is_telescope(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self):
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self):
            """GET many should return multiple when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())

        @pytest.mark.asyncio
        async def test_many_should_return_many_telescopes(self):
            """GET many should return multiple telescopes when successful"""
            res = await self.client.get(self.endpoint)
            assert all([self.is_telescope(json) for json in res.json()])

        @pytest.mark.asyncio
        async def test_many_should_return_200(self):
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
