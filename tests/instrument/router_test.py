from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, mock_instrument_data):
        self.client = async_client
        self.endpoint = "/instrument/"
        self.get_data = mock_instrument_data

    def is_instrument(self, response_json: dict) -> bool:
        """Method to validate if the api return is consistent with expected json keys"""
        instrument_return_keys = ["id", "name", "short_name", "created_on", "telescope"]
        return all(key in response_json for key in instrument_return_keys)


class TestInstrumentRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_instrument(self):
            """GET Should return created instrument when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert self.is_instrument(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self):
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self):
            """GET many should return multiple instruments when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())

        @pytest.mark.asyncio
        async def test_many_should_return_many_telescopes(self):
            """GET many should return multiple instruments when successful"""
            res = await self.client.get(self.endpoint)
            assert all([self.is_instrument(json) for json in res.json()])

        @pytest.mark.asyncio
        async def test_many_should_return_200(self):
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
