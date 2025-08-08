import uuid

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.db import models


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient) -> None:
        user_id = uuid.uuid4()
        self.client = async_client
        self.endpoint = f"/user/{user_id}/service_account/"
        self.post_data = {
            "name": "service account name",
            "description": "test service account description",
            "expiration_duration": 30,
        }


class TestServiceAccountRouter:
    class TestPost(Setup):
        @pytest.mark.asyncio
        async def test_should_return_service_account(self) -> None:
            """POST Should return created service_account when successful"""
            res = await self.client.post(self.endpoint, json=self.post_data)
            assert res.json()["description"] == self.post_data["description"]

        @pytest.mark.asyncio
        async def test_should_return_201(self) -> None:
            """POST should return 201 when successful"""
            data = {
                "name": "service account name",
                "description": "test service account description",
                "expiration_duration": 30,
            }
            res = await self.client.post(self.endpoint, json=data)
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_name(self) -> None:
            """Should return a 422 when the input is missing the name"""
            data = self.post_data
            data.pop("name")
            res = await self.client.post(self.endpoint, json=self.post_data)

            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_service_account(self) -> None:
            """GET Should return created service_account when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.get(endpoint)
            assert res.json()["description"] == "test service account description"

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many Should return multiple service_accounts when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())
            assert res.json()[0]["description"] == "test service account description"

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestUpdate(Setup):
        @pytest.mark.asyncio
        async def test_should_return_updated_service_account_on_patch(
            self, fake_service_account: models.ServiceAccount
        ) -> None:
            """Patch should return updated service account"""
            fake_service_account.name = "update_service_account_name"

            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.patch(
                endpoint, json={"name": "update_service_account_name"}
            )

            assert res.json()["name"] == "update_service_account_name"

        @pytest.mark.asyncio
        async def test_should_return_200_on_valid_service_account_patch(self) -> None:
            """Patch should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.patch(
                endpoint, json={"name": "update_service_account_name"}
            )
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestDelete(Setup):
        @pytest.mark.asyncio
        async def test_should_return_204_on_service_account_delete(self) -> None:
            """Delete should return 204 when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.delete(endpoint)
            assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
