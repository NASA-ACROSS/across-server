from unittest.mock import ANY, AsyncMock

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestLoginRoute:
    @pytest_asyncio.fixture(scope="function", autouse=True)
    async def setup(self, async_client: AsyncClient) -> None:
        self.client = async_client
        self.email = "user@example.com"
        self.endpoint = f"/auth/login?email={self.email}"

    @pytest.mark.asyncio
    async def test_should_return_200_on_success(self) -> None:
        """Should return a 200 when successful"""

        res = await self.client.post(self.endpoint)

        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_magic_link_dict_when_local(
        self, mock_config_runtime_env_is_local: AsyncMock
    ) -> None:
        """Should return a dict containing magic_link when successful"""
        mock_config_runtime_env_is_local.return_value = True
        res = await self.client.post(self.endpoint)
        response_dict = res.json()

        assert isinstance(response_dict, dict)

    @pytest.mark.asyncio
    async def test_magic_link_dict_should_contain_string(
        self, mock_config_runtime_env_is_local: AsyncMock
    ) -> None:
        """Should return a dict containing magic_link when successful"""
        mock_config_runtime_env_is_local.return_value = True
        res = await self.client.post(self.endpoint)
        response_dict = res.json()

        assert isinstance(response_dict["magic_link"], str)

    @pytest.mark.asyncio
    async def test_should_call_magic_link_generate(
        self,
        mock_magic_link_generate: AsyncMock,
    ) -> None:
        """Should generate a magic link when logging in"""
        await self.client.post(self.endpoint)

        mock_magic_link_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_verify_auth_user(
        self,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Should verify the auth user by email when logging in"""
        await self.client.post(self.endpoint)

        mock_auth_service.get_authenticated_user.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_send_login_email_to_user_when_user_is_found(
        self,
        mock_email_service: AsyncMock,
    ) -> None:
        """Should send an email to the user when logging in"""
        await self.client.post(self.endpoint)

        mock_email_service.send.assert_called_once_with(
            recipients=[ANY],
            subject="NASA ACROSS Account Login",
            content_html=ANY,
        )

    @pytest.mark.asyncio
    async def test_should_send_login_with_new_account_email_when_user_is_not_found(
        self,
        mock_email_service: AsyncMock,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Should send a 'login with new account' email to the user when not found"""
        mock_auth_service.get_authenticated_user.side_effect = fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

        await self.client.post(self.endpoint)

        mock_email_service.send.assert_called_once_with(
            recipients=[ANY],
            subject="NASA ACROSS Account Login Attempt",
            content_html=ANY,
        )

    @pytest.mark.asyncio
    async def test_should_return_error_when_get_authenticated_user_fails(
        self,
        mock_auth_service: AsyncMock,
    ) -> None:
        """Should raise a 401 error when the user is not found"""
        mock_auth_service.get_authenticated_user.side_effect = fastapi.HTTPException(
            status_code=fastapi.status.HTTP_401_UNAUTHORIZED,
        )

        res = await self.client.post(self.endpoint)

        assert res.status_code == fastapi.status.HTTP_401_UNAUTHORIZED
