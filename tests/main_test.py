import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestTopLevelRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/"

    @pytest.mark.asyncio
    async def test_should_return_200(self) -> None:
        """Should return a 200 when successful"""
        res = await self.client.get(self.endpoint)

        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_ok_as_response(self) -> None:
        """Should return an "ok" when successful"""
        res = await self.client.get(self.endpoint)

        assert res.json() == "ok"
