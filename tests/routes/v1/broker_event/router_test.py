from unittest.mock import AsyncMock
from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.broker_event.exceptions import BrokerEventNotFoundException
from across_server.routes.v1.broker_event.schemas import BrokerEvent


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/broker-event/"


class TestBrokerEventRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_broker_event(self) -> None:
            """GET Should return broker event when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert BrokerEvent.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_should_return_404_if_no_broker_event_found(
            self, mock_broker_event_service: AsyncMock
        ) -> None:
            """GET should return 404 if cannot find broker event"""
            mock_broker_event_service.get.side_effect = BrokerEventNotFoundException(
                uuid4()
            )
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND

    class TestGetMany(Setup):
        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many should return multiple when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json()["items"])

        @pytest.mark.asyncio
        async def test_many_should_return_many_broker_events(self) -> None:
            """GET many should return multiple broker events when successful"""
            res = await self.client.get(self.endpoint)
            assert all(
                [BrokerEvent.model_validate(json) for json in res.json()["items"]]
            )

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_empty_items_with_pagination_metadata(
            self,
            mock_broker_event_service: AsyncMock,
        ) -> None:
            """GET many should return empty items with pagination metadata when no results"""
            mock_broker_event_service.get_many = AsyncMock(return_value=[])  # type: ignore
            res = await self.client.get(self.endpoint)
            assert len(res.json()["items"]) == 0
