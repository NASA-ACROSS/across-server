from unittest.mock import Mock
from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.auth import magic_link


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


class TestUserPostRoute:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient, mock_user_data: dict):
        self.client = async_client
        self.endpoint = "/user/"
        self.data = mock_user_data

    @pytest.mark.asyncio
    async def test_should_send_email_when_user_is_created(self, mock_email_service):
        """Should send an email when a new user is successfully created"""
        await self.client.post(self.endpoint, json=self.data)
        mock_email_service.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_send_email_with_magic_link(self, monkeypatch):
        """Should generate magic link as part of sending email"""
        mock_magic_link_generate = Mock(return_value="mock magic link")
        monkeypatch.setattr(magic_link, "generate", mock_magic_link_generate)
        await self.client.post(self.endpoint, json=self.data)
        mock_magic_link_generate.assert_called_once()

    @pytest.mark.asyncio
    async def test_should_return_201_when_user_is_created(self):
        """Should return a 201 when a new user is successfully created"""
        res = await self.client.post(self.endpoint, json=self.data)
        assert res.status_code == fastapi.status.HTTP_201_CREATED

    @pytest.mark.asyncio
    async def test_should_catch_error_when_email_service_throws_exception(
        self, mock_email_service, capsys
    ):
        """Should catch an error and print it when email service throws an exception"""
        mock_email_service.send.side_effect = Exception("Mock raised exception")
        await self.client.post(self.endpoint, json=self.data)
        printed_error = capsys.readouterr()
        assert "Mock raised exception" in printed_error.out
