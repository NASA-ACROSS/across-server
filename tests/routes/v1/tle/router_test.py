import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestTLE:
    class TestPost:
        @pytest_asyncio.fixture(autouse=True)
        async def setup(self, async_client: AsyncClient, mock_tle_data: dict) -> None:
            self.client = async_client
            self.endpoint = "/tle/"
            self.data = mock_tle_data

        @pytest.mark.asyncio
        async def test_should_return_201_when_tle_is_created(self) -> None:
            """Should return a 201 when a new tle is successfully created"""
            res = await self.client.post(self.endpoint, json=self.data)
            assert res.status_code == fastapi.status.HTTP_201_CREATED
