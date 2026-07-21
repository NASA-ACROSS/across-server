from typing import Any
from uuid import UUID, uuid4

import fastapi
import pytest
import pytest_asyncio
from httpx import AsyncClient

from across_server.routes.v1.observation_request.schemas import ObservationRequest


class Setup:
    @pytest_asyncio.fixture(autouse=True)
    async def setup(self, async_client: AsyncClient) -> None:
        self.client = async_client
        self.endpoint = "/observation-request/"
        self.post_data = {
            "science_justification": "A clear science case",
            "object_name": "SN2026abc",
            "object_coordinates": {"ra": 123.456, "dec": -45.678},
            "object_brightness": {"value": 20.5, "unit": "mag"},
            "observation_window": {
                "begin": "2026-01-01T00:00:00Z",
                "end": "2026-01-02T00:00:00Z",
            },
            "exposure_time": 1200.0,
            "anonymize": False,
            "is_too": False,
            "instrument_id": str(uuid4()),
            "proposal_name": "Transient Follow-up",
            "proposal_code": "TRN-001",
        }
        self.post_many_data = {
            "observation_requests": [
                self.post_data.copy(),
                {
                    **self.post_data.copy(),
                    "object_name": "SN2026xyz",
                    "instrument_id": str(uuid4()),
                },
            ]
        }
        self.put_data = {
            "id": str(uuid4()),
            "science_justification": "Updated science case",
            "object_name": "SN2026abc",
            "object_coordinates": {"ra": 123.456, "dec": -45.678},
            "object_brightness": {"value": 19.0, "unit": "mag"},
            "observation_window": {
                "begin": "2026-01-01T00:00:00Z",
                "end": "2026-01-02T00:00:00Z",
            },
            "exposure_time": 1800.0,
            "anonymize": False,
            "is_too": True,
            "instrument_id": str(uuid4()),
            "status": "accepted",
            "status_reason": "Reviewed and approved",
        }
        self.put_status_data = {
            "status": "accepted",
            "status_reason": "Reviewed and approved",
        }


@pytest.fixture(params=["science_justification", "instrument_id", "observation_window"])
def required_create_field(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.fixture(params=["science_justification", "instrument_id", "object_name"])
def required_update_field(request: pytest.FixtureRequest) -> Any:
    return request.param


@pytest.fixture(params=["status"])
def required_status_update_field(request: pytest.FixtureRequest) -> Any:
    return request.param


class TestObservationRequestRouter:
    class TestGet(Setup):
        @pytest.mark.asyncio
        async def test_should_return_observation_request(self) -> None:
            """GET should return observation request when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert ObservationRequest.model_validate(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """GET should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.get(endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestGetMany(Setup):
        @pytest.mark.asyncio
        async def test_many_should_return_200_without_required_data_query(self) -> None:
            """GET many should return 200 with default pagination query values"""
            res = await self.client.get(self.endpoint)
            assert res.status_code == fastapi.status.HTTP_200_OK

    class TestPost(Setup):
        @pytest.mark.asyncio
        async def test_should_return_created_observation_request_id(self) -> None:
            """POST should return created observation request id when successful"""
            res = await self.client.post(self.endpoint, json=self.post_data)
            assert UUID(res.json())

        @pytest.mark.asyncio
        async def test_should_return_201(self) -> None:
            """POST should return 201 when successful"""
            res = await self.client.post(self.endpoint, json=self.post_data)
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(
            self, required_create_field: str
        ) -> None:
            """POST should return 422 when required fields are missing"""
            data = self.post_data.copy()
            data.pop(required_create_field)
            res = await self.client.post(self.endpoint, json=data)
            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_CONTENT

    class TestPostMany(Setup):
        @pytest.mark.asyncio
        async def test_should_return_created_observation_request_id(self) -> None:
            """POST many should return created observation request id when successful"""
            res = await self.client.post(
                self.endpoint + "bulk", json=self.post_many_data
            )
            assert all(UUID(id) for id in res.json())

        @pytest.mark.asyncio
        async def test_should_return_201(self) -> None:
            """POST many should return 201 when successful"""
            res = await self.client.post(
                self.endpoint + "bulk", json=self.post_many_data
            )
            assert res.status_code == fastapi.status.HTTP_201_CREATED

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(self) -> None:
            """POST many should return 422 when required fields are missing"""
            data = self.post_many_data.copy()
            data.pop("observation_requests")
            res = await self.client.post(self.endpoint + "bulk", json=data)
            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_CONTENT

    class TestPut(Setup):
        @pytest.mark.asyncio
        async def test_should_return_updated_observation_request_id(self) -> None:
            """PUT should return updated observation request id when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.put(endpoint, json=self.put_data)
            assert UUID(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """PUT should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.put(endpoint, json=self.put_data)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(
            self, required_update_field: str
        ) -> None:
            """PUT should return 422 when required fields are missing"""
            endpoint = self.endpoint + f"{uuid4()}"
            data = self.put_data.copy()
            data.pop(required_update_field)
            res = await self.client.put(endpoint, json=data)
            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_CONTENT

    class TestDelete(Setup):
        @pytest.mark.asyncio
        async def test_should_return_204_on_delete(self) -> None:
            """DELETE should return 204 when successful"""
            endpoint = self.endpoint + f"{uuid4()}"
            res = await self.client.delete(endpoint)
            assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT

    class TestPutStatus(Setup):
        @pytest.mark.asyncio
        async def test_should_return_updated_observation_request_id(self) -> None:
            """PUT status should return updated observation request id when successful"""
            endpoint = self.endpoint + f"{uuid4()}/status"
            res = await self.client.put(endpoint, json=self.put_status_data)
            assert UUID(res.json())

        @pytest.mark.asyncio
        async def test_should_return_200(self) -> None:
            """PUT status should return 200 when successful"""
            endpoint = self.endpoint + f"{uuid4()}/status"
            res = await self.client.put(endpoint, json=self.put_status_data)
            assert res.status_code == fastapi.status.HTTP_200_OK

        @pytest.mark.asyncio
        async def test_should_return_422_when_missing_required_fields(
            self, required_status_update_field: str
        ) -> None:
            """PUT status should return 422 when required fields are missing"""
            endpoint = self.endpoint + f"{uuid4()}/status"
            data = self.put_status_data.copy()
            data.pop(required_status_update_field)
            res = await self.client.put(endpoint, json=data)
            assert res.status_code == fastapi.status.HTTP_422_UNPROCESSABLE_CONTENT
