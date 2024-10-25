from unittest import mock
import fastapi
import pytest
import pytest_asyncio

from httpx import AsyncClient
from unittest.mock import AsyncMock


class TestLoginRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient):
        self.client = async_client
        self.email = "user@example.com"
        self.endpoint = f"/auth/login?email={self.email}"

    @pytest.mark.asyncio
    async def test_should_return_200_on_success(self):
        """Should return a 200 when successful"""

        res = await self.client.post(self.endpoint)

        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_call_magic_link_generate(
        self,
        mock_magic_link_generate: AsyncMock,
    ):
        """Should generate a magic link when logging in"""
        await self.client.post(self.endpoint)

        mock_magic_link_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_verify_auth_user(
        self,
        mock_auth_service,
    ):
        """Should verify the auth user by email when logging in"""
        await self.client.post(self.endpoint)

        mock_auth_service.get_authenticated_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_send_email_to_user(
        self,
        mock_email_service,
    ):
        """Should send an email to the user when logging in"""
        await self.client.post(self.endpoint)

        mock_email_service.send.assert_called_once()
        mock_email_service.send.assert_called_with(self.email, mock.ANY, mock.ANY)
