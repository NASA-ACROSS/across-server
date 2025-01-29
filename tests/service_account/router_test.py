from __future__ import annotations

import json
import uuid

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient):
        self.client = async_client
        self.endpoint = "/user/service_account/"
        self.post_data = {
            "name": "service account name",
            "description": "test service account description",
            "expiration_duration": 30,
        }


class TestServiceAccountRouter:
    class TestPost(Setup):
        @pytest.mark.asyncio
        async def test_should_return_service_account(self):
            """POST Should return created service_account when successful"""
            res = await self.client.post(self.endpoint, json=self.post_data)
            assert json.loads(res.text)["description"] == self.post_data["description"]

        @pytest.mark.asyncio
        async def test_should_return_201(self, mock_service_account_data):
            """POST should return 201 when successful"""
            data = {
                "name": "service account name",
                "description": "test service account description",
                "expiration_duration": 30,
            }
            res = await self.client.post(self.endpoint, json=data)
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_name(self):
            """Should return a 422 when the input is missing the name"""
            data = self.post_data
            data.pop("name")
            res = await self.client.post(self.endpoint, json=self.post_data)

            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_service_account(self):
            """GET Should return created service_account when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.get(endpoint)
            assert (
                json.loads(res.text)["description"]
                == "test service account description"
            )

        @pytest.mark.asyncio
        async def test_should_return_200(self):
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self):
            """GET many Should return multiple service_accounts when successful"""
            res = await self.client.get(self.endpoint)
            assert len(json.loads(res.text))
            assert (
                json.loads(res.text)[0]["description"]
                == "test service account description"
            )

        @pytest.mark.asyncio
        async def test_many_should_return_200(self):
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestUpdate(Setup):
        @pytest.mark.asyncio
        async def test_should_return_updated_service_account_on_patch(
            self, mock_service_account_service
        ):
            """Patch should return updated service account"""
            mock_service_account_service.update.return_value["name"] = (
                "update_service_account_name"
            )
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.patch(
                endpoint, json={"name": "update_service_account_name"}
            )
            assert json.loads(res.text)["name"] == "update_service_account_name"

        @pytest.mark.asyncio
        async def test_should_return_200_on_valid_service_account_patch(self):
            """Patch should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.patch(
                endpoint, json={"name": "update_service_account_name"}
            )
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestDelete(Setup):
        @pytest.mark.asyncio
        async def test_should_return_204_on_service_account_delete(self):
            """Delete should return 204 when successful"""
            endpoint = self.endpoint + f"{uuid.uuid4()}"
            res = await self.client.delete(endpoint)
            assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
