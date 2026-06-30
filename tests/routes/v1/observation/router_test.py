from collections.abc import Generator
from unittest.mock import AsyncMock
from uuid import uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.db.models import Observation as ObservationModel
from across_server.routes.v1.observation.schemas import Observation


class Setup:
    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup(
        self,
        async_client: AsyncClient,
        fake_observation_data_with_footprint: ObservationModel,
    ) -> None:
        self.client = async_client
        self.endpoint = "/observation/"
        self.get_data = fake_observation_data_with_footprint


class SetupMany:
    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup(
        self, async_client: AsyncClient, fake_observation_many: None
    ) -> None:
        self.client = async_client
        self.endpoint = "/observation/"
        self.get_data = fake_observation_many


class SetupOverlapPoint:
    @pytest_asyncio.fixture(autouse=True, scope="function")
    async def setup(
        self, async_client: AsyncClient, fake_observation_contains_point_many: None
    ) -> None:
        self.client = async_client
        self.endpoint = "/observation/search/contains-point/"
        self.get_data = fake_observation_contains_point_many


class TestObservationRouterGet:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observation(self) -> None:
            """GET Should return created observation when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert Observation.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestGetMany(SetupMany):
        @pytest.mark.asyncio
        async def test_many_should_return_many(self) -> None:
            """GET many should return multiple when successful"""
            res = await self.client.get(self.endpoint)
            assert len(res.json())

        @pytest.mark.asyncio
        async def test_many_should_return_many_observations(self) -> None:
            """GET many should return multiple observations when successful"""
            res = await self.client.get(self.endpoint)
            assert all([Observation.model_validate(obs) for obs in res.json()["items"]])

        @pytest.mark.asyncio
        async def test_many_should_return_200(self) -> None:
            """GET many should return 200 when successful"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_many_should_return_empty_items_with_pagination_metadata(
            self, mock_observation_service: Generator[AsyncMock]
        ) -> None:
            """GET many should return empty items with pagination metadata when no results"""
            mock_observation_service.get_many = AsyncMock(return_value=([], 0))  # type: ignore
            res = await self.client.get(self.endpoint)
            assert len(res.json()["items"]) == 0

        @pytest.mark.asyncio
        async def test_many_should_return_footprints_when_include_footprints_is_true(
            self,
        ) -> None:
            """GET many should return footprints when include_footprints parameter set to true"""
            res = await self.client.get(self.endpoint + "?include_footprints=true")
            observation = res.json()["items"][0]
            assert len(observation["footprint"]) > 0

        @pytest.mark.asyncio
        async def test_many_should_not_return_footprints_when_include_footprints_is_false(
            self,
        ) -> None:
            """GET many should return footprints when include_footprints parameter set to false"""
            res = await self.client.get(self.endpoint + "?include_footprints=false")
            observation = res.json()["items"][0]
            assert len(observation["footprint"]) == 0


class TestObservationRouterOverlapPoint:
    class TestOverlapPoint(SetupOverlapPoint):
        @pytest.mark.asyncio
        async def test_overlap_point_should_return_200(self) -> None:
            """GET overlap-point should return 200 when successful"""
            res = await self.client.get(self.endpoint + "?ra=123.456&dec=-87.65")
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_overlap_point_should_return_observations(self) -> None:
            """GET overlap-point should return list of observations when successful"""
            res = await self.client.get(self.endpoint + "?ra=123.456&dec=-87.65")
            assert all([Observation.model_validate(obs) for obs in res.json()["items"]])

        @pytest.mark.asyncio
        async def test_overlap_point_should_return_empty_items_with_pagination_metadata(
            self, mock_observation_service: Generator[AsyncMock]
        ) -> None:
            """GET overlap-point should return empty items with pagination metadata when no results"""
            mock_observation_service.get_contains_point = AsyncMock(
                return_value=([], 0)
            )  # type: ignore
            res = await self.client.get(self.endpoint + "?ra=123.456&dec=-87.65")
            assert len(res.json()["items"]) == 0

        @pytest.mark.asyncio
        @pytest.mark.parametrize(
            "query",
            [
                "?dec=0",  # missing ra
                "?ra=0",  # missing dec
                "?ra=360&dec=0",  # ra out of range
                "?ra=0&dec=91",  # dec out of range
                "?ra=0&dec=0&instrument_ids=not-a-uuid",  # invalid uuid
            ],
        )
        async def test_overlap_point_should_return_422_when_params_invalid(
            self, query: str
        ) -> None:
            """GET overlap-point should return 422 when any parameters are invalid"""
            res = await self.client.get(self.endpoint + query)
            assert res.status_code == 422
