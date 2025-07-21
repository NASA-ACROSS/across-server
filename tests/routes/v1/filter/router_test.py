from unittest.mock import AsyncMock
from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.filter.schemas import Filter


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self, async_client: AsyncClient, mock_filter_data: AsyncMock
    ) -> None:
        self.client = async_client
        self.endpoint = "/filter/"
        self.get_data = mock_filter_data


class TestFilterRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_filter(self) -> None:
            """GET Should return created filter when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert Filter.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many should return multiple filters when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())

        @pytest.mark.asyncio
        async def test_many_should_return_many_filters(self) -> None:
            """GET many should return multiple filters when successful"""
            res = await self.client.get(self.endpoint)
            assert all([Filter.model_validate(json) for json in res.json()])

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK
