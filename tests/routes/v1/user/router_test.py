from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class TestUserPatchRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/user/" + str(uuid4())

    @pytest.mark.asyncio
    async def test_should_return_200_when_modifying_first_name(self) -> None:
        """Should return a 200 when successfully modifying user's first name"""
        res = await self.client.patch(
            self.endpoint,
            json={"first_name": "Sandy"},
        )
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_200_when_modifying_last_name(self) -> None:
        """Should return a 200 when successfully modifying user's last name"""
        res = await self.client.patch(
            self.endpoint,
            json={"last_name": "Cheeks"},
        )
        assert res.status_code == fastapi.status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_should_return_200_when_modifying_username(self) -> None:
        """Should return a 200 when successfully modifying user's username"""
        res = await self.client.patch(
            self.endpoint,
            json={"username": "sandy_cheeks"},
        )
        assert res.status_code == fastapi.status.HTTP_200_OK


class TestUserPostRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, mock_user_json: dict) -> None:
        self.client = async_client
        self.endpoint = "/user/"
        self.data = mock_user_json

    @pytest.mark.asyncio
    async def test_should_send_email_when_user_is_created(
        self, mock_email_service: MagicMock
    ) -> None:
        """Should send an email when a new user is successfully created"""
        await self.client.post(self.endpoint, json=self.data)
        mock_email_service.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_send_email_with_magic_link(
        self, mock_auth_service: MagicMock
    ) -> None:
        """Should generate magic link as part of sending email"""
        await self.client.post(self.endpoint, json=self.data)
        mock_auth_service.generate_magic_link.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_201_when_user_is_created(self) -> None:
        """Should return a 201 when a new user is successfully created"""
        res = await self.client.post(self.endpoint, json=self.data)
        assert res.status_code == fastapi.status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_should_catch_error_when_email_service_throws_exception(
        self, mock_email_service: MagicMock
    ) -> None:
        """Should catch an error and print it when email service throws an exception"""
        mock_email_service.send.side_effect = Exception("Mock raised exception")

        with patch("across_server.routes.v1.user.router.logger") as log_mock:
            await self.client.post(self.endpoint, json=self.data)
            assert "Email service failed" in log_mock.error.call_args.args[0]

    @pytest.mark.asyncio
    async def test_should_return_magic_link_dict_when_local(
        self, mock_config_runtime_env_is_local: AsyncMock
    ) -> None:
        """Should return a dict when local"""
        mock_config_runtime_env_is_local.return_value = True
        res = await self.client.post(self.endpoint, json=self.data)
        response_dict = res.json()

        assert isinstance(response_dict, dict)

    @pytest.mark.asyncio
    async def test_should_contain_magic_link_string(
        self, mock_config_runtime_env_is_local: AsyncMock
    ) -> None:
        """Should return a dict containing magic_link string when local"""
        mock_config_runtime_env_is_local.return_value = True
        res = await self.client.post(self.endpoint, json=self.data)
        response_dict = res.json()

        assert isinstance(response_dict["magic_link"], str)
