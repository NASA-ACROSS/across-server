from typing import Any
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.broker_alert.exceptions import (
    BrokerAlertNotFoundException,
)
from across_server.routes.v1.broker_alert.schemas import BrokerAlert


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(
        self,
        async_client: AsyncClient,
    ) -> None:
        self.client = async_client
        self.endpoint = "/broker-alert/"


class TestBrokerAlertRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_broker_alert(self) -> None:
            """GET Should return broker alert when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert BrokerAlert.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_should_return_404_if_no_broker_alert_found(
            self, mock_broker_alert_service: AsyncMock
        ) -> None:
            """GET should return 404 if cannot find broker alert"""
            mock_broker_alert_service.get.side_effect = BrokerAlertNotFoundException(
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
        async def test_many_should_return_many_broker_alerts(self) -> None:
            """GET many should return multiple broker alerts when successful"""
            res = await self.client.get(self.endpoint)
            assert all(
                [BrokerAlert.model_validate(json) for json in res.json()["items"]]
            )

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_empty_items_with_pagination_metadata(
            self,
            mock_broker_alert_service: AsyncMock,
        ) -> None:
            """GET many should return empty items with pagination metadata when no results"""
            mock_broker_alert_service.get_many = AsyncMock(return_value=[])  # type: ignore
            res = await self.client.get(self.endpoint)
            assert len(res.json()["items"]) == 0

    class TestPost(Setup):
        @pytest.mark.asyncio
        async def test_should_return_201(
            self, fake_broker_alert_post_data: dict
        ) -> None:
            """POST should return 201 when successful"""
            res = await self.client.post(
                self.endpoint, json=fake_broker_alert_post_data
            )
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_created_broker_alert_id(
            self, fake_broker_alert_post_data: dict
        ) -> None:
            """POST should return created broker alert ID when successful"""
            res = await self.client.post(
                self.endpoint, json=fake_broker_alert_post_data
            )
            assert UUID(res.json())

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(
            self, required_fields: Any, fake_broker_alert_post_data: dict
        ) -> None:
            """Should return a 422 when the input is missing required fields"""
            fake_broker_alert_post_data.pop(required_fields)
            res = await self.client.post(
                self.endpoint, json=fake_broker_alert_post_data
            )

            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_CONTENT
