from typing import Any
from uuid import UUID, uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.db.models import Schedule as ScheduleModel


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
        mock_schedule_post_data: dict,
        mock_schedule_data: ScheduleModel,
        mock_schedule_post_many_data: dict,
    ) -> None:
        self.client = async_client
        self.endpoint = "/schedule/"
        self.post_data = mock_schedule_post_data
        self.get_data = mock_schedule_data
        self.post_many_data = mock_schedule_post_many_data


class TestScheduleRouter:
    class TestPost(Setup):
        @pytest.mark.asyncio
        async def test_should_return_201(self) -> None:
            """POST should return 201 when successful"""
            res = await self.client.post(self.endpoint, json=self.post_data)
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_created_schedule_id(self) -> None:
            """POST Should return created service_account when successful"""
            res = await self.client.post(self.endpoint, json=self.post_data)
            assert UUID(res.json())

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(
            self, required_fields: Any
        ) -> None:
            """Should return a 422 when the input is missing the name"""
            self.post_data.pop(required_fields)
            res = await self.client.post(self.endpoint, json=self.post_data)

            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY

    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_schedule(self) -> None:
            """GET Should return created service_account when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.json()["name"] == "Test Schedule"

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many should return multiple schedules when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json()["items"])
            assert res.json()["items"][0]["name"] == "Test Schedule"

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_history_should_return_many(self) -> None:
            """GET history should return multiple schedules when successful"""
            res = await self.client.get(self.endpoint + "history")
            assert len(res.json()["items"])
            assert res.json()["items"][0]["name"] == "Test Schedule"

        @pytest.mark.asyncio
        async def test_history_should_return_200(self) -> None:
            """GET history should return 200 when successful"""
            res = await self.client.get(self.endpoint + "history")
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestPostMany(Setup):
        @pytest.mark.asyncio
        async def test_should_return_201_when_successful(self) -> None:
            """Post Many should return 201 when successful"""
            res = await self.client.post(
                self.endpoint + "many", json=self.post_many_data
            )
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_list_when_successful(self) -> None:
            """Post Many should return list when successful"""
            res = await self.client.post(
                self.endpoint + "many", json=self.post_many_data
            )
            assert isinstance(res.json(), list)

        @pytest.mark.asyncio
        async def test_should_return_ids_when_successful(self) -> None:
            """Post Many should return list of IDs when successful"""
            res = await self.client.post(
                self.endpoint + "many", json=self.post_many_data
            )
            assert all([UUID(element) for element in res.json()])

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(
            self, required_fields: Any
        ) -> None:
            """Should return a 422 when any input schedule is missing a required field"""
            self.post_many_data["schedules"][0].pop(required_fields)
            res = await self.client.post(
                self.endpoint + "many", json=self.post_many_data
            )

            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_ENTITY
