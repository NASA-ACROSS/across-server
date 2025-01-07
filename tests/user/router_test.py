import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient
from uuid import uuid4

class TestUserPatchRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self, 
        async_client: AsyncClient,
    ):
        self.client = async_client
        self.endpoint = "/user/" + str(uuid4())

    @pytest.mark.asyncio
    async def test_should_return_200_when_modifying_first_name(self):
        """Should return a 200 when successfully modifying user's first name"""
        res = await self.client.patch(
            self.endpoint, 
            json={"first_name": "Sandy"},
        )
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_200_when_modifying_last_name(self):
        """Should return a 200 when successfully modifying user's last name"""
        res = await self.client.patch(
            self.endpoint, 
            json={"last_name": "Cheeks"},
        )
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_200_when_modifying_username(self):
        """Should return a 200 when successfully modifying user's username"""
        res = await self.client.patch(
            self.endpoint, 
            json={"username": "sandy_cheeks"},
        )
        assert res.status_code == fastapi.status.HTTP_200_OK